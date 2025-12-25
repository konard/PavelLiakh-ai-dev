import unittest
from unittest.mock import Mock, MagicMock, patch

from src.app.domain.story import Story, NEW_STATE
from src.app.service.story_service import StoryService
from src.infrastructure.github.issues_client import (
    GithubIssue,
    TODO_LABEL,
    IN_PROGRESS_LABEL,
)


class TestStoryService(unittest.TestCase):
    def setUp(self):
        self.issues_client = Mock()
        self.story_storage = Mock()
        self.log = Mock()
        self.service = StoryService(self.issues_client, self.story_storage, self.log)

    def test_get_new_stories(self):
        expected_stories = [
            Story(number=1, name="Story 1", state=NEW_STATE),
            Story(number=2, name="Story 2", state=NEW_STATE),
        ]
        self.story_storage.get_stories_by_state.return_value = expected_stories

        result = self.service.get_new_stories()

        assert result == expected_stories
        self.story_storage.get_stories_by_state.assert_called_once_with(NEW_STATE)

    def test_check_for_update_with_todo_label_new_issue(self):
        issue = GithubIssue(
            number=123,
            title="Test Issue",
            body="Test description",
            labels=[TODO_LABEL, "bug"],
            comments=["Comment 1"],
        )

        self.story_storage.get_story.return_value = None
        saved_story = Story(
            number=123, name="Test Issue", description="Test description", state=NEW_STATE
        )
        self.story_storage.save_story.return_value = saved_story

        result = self.service.check_for_update(issue)

        assert result == saved_story
        self.story_storage.get_story.assert_called_once_with(123)
        self.story_storage.save_story.assert_called_once()
        self.issues_client.update_issue_labels.assert_called_once_with(
            issue_number=123, new_labels=[IN_PROGRESS_LABEL]
        )

    def test_check_for_update_with_todo_label_existing_issue(self):
        issue = GithubIssue(
            number=123,
            title="Test Issue",
            body="Test description",
            labels=[TODO_LABEL],
            comments=[],
        )

        existing_story = Story(number=123, name="Old name", state=NEW_STATE)
        self.story_storage.get_story.return_value = existing_story

        saved_story = Story(
            number=123, name="Test Issue", description="Test description", state=NEW_STATE
        )
        self.story_storage.save_story.return_value = saved_story

        result = self.service.check_for_update(issue)

        assert result == saved_story
        self.story_storage.save_story.assert_called_once()
        self.issues_client.update_issue_labels.assert_called_once_with(
            issue_number=123, new_labels=[IN_PROGRESS_LABEL]
        )

    def test_check_for_update_without_todo_label(self):
        issue = GithubIssue(
            number=123,
            title="Test Issue",
            body="Test description",
            labels=["bug", "enhancement"],
            comments=[],
        )

        result = self.service.check_for_update(issue)

        assert result is None
        self.story_storage.save_story.assert_not_called()
        self.issues_client.update_issue_labels.assert_not_called()

    def test_convert_github_issue(self):
        issue = GithubIssue(
            number=456,
            title="Convert Test",
            body="Body content",
            labels=["label1"],
            comments=["comment1", "comment2"],
        )

        story = self.service._convert_github_issue(issue)

        assert story.number == 456
        assert story.name == "Convert Test"
        assert story.description == "Body content"
        assert story.comments == ["comment1", "comment2"]
        assert story.state == NEW_STATE

    def test_convert_github_issue_with_none_body(self):
        issue = GithubIssue(
            number=789, title="No Body", body=None, labels=[], comments=[]
        )

        story = self.service._convert_github_issue(issue)

        assert story.number == 789
        assert story.name == "No Body"
        assert story.description == ""
        assert story.comments == []
        assert story.state == NEW_STATE


if __name__ == "__main__":
    unittest.main()
