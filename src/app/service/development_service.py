"""This service is used to manage the development of the application."""

from src.app.domain.story import Story, DEVELOPMENT_STATE
from src.app.service.planner_service import PlannerService
from src.config import config
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.cicd.code_builder import CodeBuilder
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
        story_storage: StoryStorage,
        log,
    ):
        self.llm_client = llm_client
        self.log = log
        self.git_repo_client = git_repo_client
        self.planner_service = planner_service
        self.code_builder = code_builder
        self.story_storage = story_storage

    def implement(self, story: Story):
        self.planner_service.plan(story)
        story.state = DEVELOPMENT_STATE
        self.story_storage.save_story(story)

        repository_context = self._get_repo_context(story)
        self._add_plan_to_repo(story, repository_context)

        check_result = self.code_builder.check_commit(repository_context)
        if check_result.success:
            self.log.info(f"Code check passed for story {story.number}.")
        else:
            self.log.error(
                f"Code check failed for story {story.number}: {check_result.error_message}"
            )

    def _get_repo_context(self, story: Story) -> RepoContext:
        return RepoContext(
            name=config.github_repo_name,
            local_path=config.workspace_path / config.github_repo_name,
            branch=f"{BRANCH_PREFIX}{story.number}",
            token=config.github_api_key,
        )

    def _add_plan_to_repo(self, story: Story, repository_context: RepoContext) -> None:
        plan_as_string = "\n".join(story.plan)
        self.git_repo_client.checkout_branch(repository_context)
        self.git_repo_client.patch_file(repository_context, "plan.md", plan_as_string, "Add plan")
        self.git_repo_client.push_changes(repository_context)
        self.git_repo_client.open_pr(repository_context)
