from src.app.domain.story import Story
from src.infrastructure.github.issues_client import IssuesClient, GithubIssue
from src.infrastructure.logger import get_logger

class StoryService:
    def __init__(self, issues_client: IssuesClient, log=None):
        self.issues_client = issues_client
        self.log = log or get_logger(__name__)

    def check_for_update(self, issue: GithubIssue) -> Story:
        """Check and process GitHub issue updates"""
        if not any(label.name == 'TODO' for label in issue.labels):
            self.log.debug(f"Issue {issue.number} doesn't have TODO label, skipping")
            return None

        story = self._convert_github_issue(issue)
        # TODO: Add DB check and update logic here
        # TODO: Update GitHub issue labels to IN_PROGRESS
        
        return story

    def _convert_github_issue(self, issue: GithubIssue) -> Story:
        return Story(
            number=issue.number,
            name=issue.title,
            description=issue.body or "",
            comments=[comment.body for comment in issue.get_comments()],
            state=issue.state,
        )
