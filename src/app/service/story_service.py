from typing import Optional

from src.app.domain.story import Story, NEW_STATE, DEVELOPMENT_STATE
from src.infrastructure.github.issues_client import IssuesClient, GithubIssue, IN_PROGRESS_LABEL, TODO_LABEL
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.logger import get_logger


class StoryService:
    def __init__(self, issues_client: IssuesClient, story_storage: StoryStorage, log=None):
        self.issues_client = issues_client
        self.story_storage = story_storage
        self.log = log or get_logger(__name__)

    def get_new_stories(self) -> list[Story]:
        return self.story_storage.get_stories_by_state(NEW_STATE)

    def check_for_update(self, issue: GithubIssue) -> Optional[Story]:
        if not any(label.upper() == TODO_LABEL for label in issue.labels):
            self.log.debug(f"Issue #{issue.number} doesn't have TODO label, skipping")
            return None

        story = self._convert_github_issue(issue)
        existing_story = self.story_storage.get_story(issue.number)

        saved_story = self.story_storage.save_story(story)
        self.issues_client.update_issue_labels(
            issue_number=issue.number, new_labels=[IN_PROGRESS_LABEL]
        )
        self.log.info(
            f"Processed {'new' if not existing_story else 'updated'} TODO issue #{issue.number}: {issue.title}"
        )

        return saved_story

    def _convert_github_issue(self, issue: GithubIssue) -> Story:
        return Story(
            number=issue.number,
            name=issue.title,
            description=issue.body or "",
            comments=issue.comments,
            state=NEW_STATE,
        )
