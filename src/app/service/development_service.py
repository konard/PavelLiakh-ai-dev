"""This service is used to manage the development of the application."""

from src.app.domain.story import Story
from src.config import config
from src.infrastructure.github.git_repo_client import RepoContext

BRANCH_PREFIX = "ai-dev_story-"


class DevelopmentService:
    def __init__(self, llm_client, git_repo_client, code_builder, planner_service, log):
        self.llm_client = llm_client
        self.log = log
        self.git_repo_client = git_repo_client
        self.planner_service = planner_service
        self.code_builder = code_builder

    def implement(self, story: Story):
        plan = self.planner_service.plan(story)
        story.plan = plan.plan
        repository_context = self._get_repo_context(story)
        self._add_plan_to_repo(story, repository_context)
        self.code_builder.check_commit(repository_context)

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
