from src.app.domain.story import Story
from src.app.service.planner_service import PlannerService
from src.infrastructure.cicd.code_builder import CodeBuilder
from src.infrastructure.github.issues_client import IssuesClient


class StoryWorkflow:
    def __init__(self,
                 issues_client: IssuesClient,
                 planner_service: PlannerService,
                 code_builder: CodeBuilder,):
        self.issues_client = issues_client
        self.planner_service = planner_service
        self.code_builder = code_builder

    # FIXME add a trigger. Must be launched 10 times a minute
    def find_updates(self) -> bool:
        issues = self.issues_client.get_opened_issues()
        for issue in issues:
            self._check_for_update(issue)

    def build_plan(self, story):
        """Convert GitHub issue to story and save it in the DB"""
        commit = self.planner_service.plan(story)
        plan_path = self.planner_service.get_plan_path(story)
        self.code_builder.build_code()
        pass

    def _check_for_update(self, issue):
        # FIXME implement this
        # check if issue has label `TODO`
        # convert github issue to story
        # check if the issue is already in the DB
        # if not, add it to the DB. Change label in github with `IN_PROGRESS` and update issue in github
        # if yes, update the issue in the DB
        pass

    def _convert_github_issue(self, issue) -> Story:
        return Story(
            number=issue.number,
            name=issue.title,
            description=issue.body or "",
            comments=[comment.body for comment in issue.get_comments()],
            state=issue.state,
        )

    def _convert_github_issue(self, issue: Issue) -> GithubIssue:
        """Convert PyGithub Issue to our GitHubIssue dataclass"""
        return GithubIssue(
            title=issue.title,
            number=issue.number,
            state=issue.state,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
            created_at=issue.created_at.isoformat(),
            updated_at=issue.updated_at.isoformat(),
            url=issue.html_url
        )