from src.app.domain.story import Story
from src.app.service.planner_service import PlannerService
from src.app.service.story_service import StoryService
from src.config import config
from src.infrastructure.cicd.code_builder import CodeBuilder
from src.infrastructure.github.git_repo_client import RepoContext, GitRepoClient
from src.infrastructure.github.issues_client import IssuesClient


class StoryWorkflow:
    def __init__(
        self,
        issues_client: IssuesClient,
        planner_service: PlannerService,
        code_builder: CodeBuilder,
        story_service: StoryService,
        git_repo_client: GitRepoClient,
        log,
    ):
        self.issues_client = issues_client
        self.planner_service = planner_service
        self.code_builder = code_builder
        self.story_service = story_service
        self.git_repo_client = git_repo_client
        self.log = log

    def find_updates(self) -> None:
        issues = self.issues_client.get_opened_issues()
        self.log.info(f"Checking {len(issues)} open issues for updates")
        for issue in issues:
            self._check_for_update(issue)

    def plan(self):
        new_stories = self.story_service.get_new_stories()
        for story in new_stories:
            self.log.info(f"Planning story {story.name}")
            self._add_plan_to_repo(story)

    def _add_plan_to_repo(self, story: Story):
        plan = self.planner_service.plan(story)
        repository_context = RepoContext(
            name=config.github_repo_name,
            local_path=config.workspace_path / config.github_repo_name,
            branch="story_branch",
            token=config.github_api_key,
        )
        self.git_repo_client.checkout_branch(repository_context)
        plan_as_string = "\n".join(plan.plan)
        self.git_repo_client.patch_file(repository_context, "plan.md", plan_as_string, "Add plan")
        self.git_repo_client.push_changes(repository_context)
        self.code_builder.check_commit(repository_context)
        self.git_repo_client.open_pr(repository_context)

    def _check_for_update(self, issue):
        story = self.story_service.check_for_update(issue)
        if story:
            self._add_plan_to_repo(story)
