"""This service is used to manage the development of the application."""

from src.app.domain.story import Story, DEVELOPMENT_STATE
from src.app.service.planner_service import PlannerService
from src.app.service.code_request_service import CodeRequestService
from src.config import config
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ci.code_builder import CodeBuilder
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.github.repository_client import RepoContext, RepositoryClient

BRANCH_PREFIX = "ai-dev_story-"


class DevelopmentService:
    def __init__(
        self,
        llm_client: LlmClient,
        git_repo_client: RepositoryClient,
        code_builder: CodeBuilder,
        planner_service: PlannerService,
        code_request_service: CodeRequestService,
        story_storage: StoryStorage,
        log,
    ):
        self.llm_client = llm_client
        self.log = log
        self.git_repo_client = git_repo_client
        self.planner_service = planner_service
        self.code_request_service = code_request_service
        self.code_builder = code_builder
        self.story_storage = story_storage

    def implement(self, story: Story):
        self.planner_service.plan(story)
        self.code_request_service.implement(story)
        story.state = DEVELOPMENT_STATE
        self.story_storage.save_story(story)

        repository_context = self._get_repo_context(story)
        self._add_plan_to_repo(story, repository_context)
        self._add_generated_code_to_repo(story, repository_context)
        self.git_repo_client.make_commit(
            repository_context, f"Implement story {story.number}: {story.name}"
        )

        check_result = self.code_builder.check_commit(repository_context)
        if check_result.success:
            self.log.info(f"Code check passed for story {story.number}: {check_result.stdout}")
            self.git_repo_client.push_changes(repository_context)
            self._open_pr(story, repository_context)
        else:
            self.log.error(f"Code check failed for story {story.number}: {check_result.stderr}")

    def _get_repo_context(self, story: Story) -> RepoContext:
        return RepoContext(name=config.github_repo_name, branch=f"{BRANCH_PREFIX}{story.number}")

    def _add_plan_to_repo(self, story: Story, repository_context: RepoContext) -> None:
        plan_as_string = "\n".join(story.plan)
        plan_filename = f"generated_plans/issue_{story.number}_plan.md"
        self.git_repo_client.checkout_branch(repository_context)
        self.git_repo_client.patch_file(
            repository_context, plan_filename, plan_as_string
        )

    def _add_generated_code_to_repo(self, story: Story, repository_context: RepoContext) -> None:
        self.git_repo_client.checkout_branch(repository_context)

        for filename, content in story.code_files.items():
            self.git_repo_client.patch_file(
                repository_context,
                filename,
                content,
            )

    def _open_pr(self, story: Story, repository_context: RepoContext) -> None:
        pr_link = self.git_repo_client.open_pr(repository_context)
        self.log.info(f"Pull request created: {pr_link}")
        story.pr_link = pr_link
        self.story_storage.save_story(story)
