from typing import Optional

from src.app.domain.story import Story, NEW_STATE
from src.infrastructure.github.issues_client import IssuesClient, GithubIssue
from src.infrastructure.logger import get_logger


class StoryService:
    def __init__(self, issues_client: IssuesClient, log=None):
        self.issues_client = issues_client
        self.log = log or get_logger(__name__)

    def check_for_update(self, issue: GithubIssue) -> Optional[Story]:
        """Check and process GitHub issue updates"""
        if not any(label.upper() == "TODO" for label in issue.labels):
            self.log.debug(f"Issue #{issue.number} doesn't have TODO label, skipping")
            return None

        story = self._convert_github_issue(issue)
        self.log.info(f"Processing new TODO issue #{issue.number}: {issue.title}")
        # TODO: Add DB check and update logic here
        # TODO: Update GitHub issue labels to IN_PROGRESS

        return story

    def _convert_github_issue(self, issue: GithubIssue) -> Story:
        return Story(
            number=issue.number,
            name=issue.title,
            description=issue.body or "",
            comments=issue.comments,
            state=NEW_STATE,
        )
