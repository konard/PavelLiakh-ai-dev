import unittest
from unittest.mock import Mock

from src.app.domain.story import Story, NEW_STATE
from src.app.service.story_service import StoryService
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.github.issues_client import GithubIssue, TODO_LABEL
from tests.helper.db_helper import reset_storage


class TestStoryWorkflowIntegration(unittest.TestCase):
    """Integration tests for the story workflow from GitHub issue to stored story"""

    def setUp(self):
        reset_storage()
        self.log = Mock()
        self.storage = JsonStorage()
        self.story_storage = StoryStorage(self.storage, self.log)
        self.issues_client = Mock()
        self.story_service = StoryService(
            self.issues_client, self.story_storage, self.log
        )

    def tearDown(self):
        reset_storage()

    def test_create_and_retrieve_story(self):
        issue = GithubIssue(
            number=1,
            title="Test Issue",
            body="Description",
            labels=[TODO_LABEL],
            comments=["Comment 1"],
        )

        created_story = self.story_service.check_for_update(issue)

        assert created_story is not None
        assert created_story.number == 1
        assert created_story.name == "Test Issue"
        assert created_story.state == NEW_STATE

        retrieved_story = self.story_storage.get_story(1)
        assert retrieved_story is not None
        assert retrieved_story.number == created_story.number
        assert retrieved_story.name == created_story.name

    def test_update_existing_story(self):
        issue1 = GithubIssue(
            number=2,
            title="Original Title",
            body="Original body",
            labels=[TODO_LABEL],
            comments=[],
        )
        self.story_service.check_for_update(issue1)

        issue2 = GithubIssue(
            number=2,
            title="Updated Title",
            body="Updated body",
            labels=[TODO_LABEL],
            comments=["New comment"],
        )
        updated_story = self.story_service.check_for_update(issue2)

        assert updated_story.name == "Updated Title"
        assert updated_story.description == "Updated body"
        assert "New comment" in updated_story.comments

        stories = self.story_storage.get_all()
        assert len(stories) == 1

    def test_get_new_stories_filters_by_state(self):
        issue1 = GithubIssue(number=10, title="Issue 10", labels=[TODO_LABEL])
        issue2 = GithubIssue(number=11, title="Issue 11", labels=[TODO_LABEL])

        self.story_service.check_for_update(issue1)
        self.story_service.check_for_update(issue2)

        new_stories = self.story_service.get_new_stories()

        assert len(new_stories) == 2
        assert all(story.state == NEW_STATE for story in new_stories)

    def test_multiple_stories_persistence(self):
        for i in range(5):
            issue = GithubIssue(
                number=100 + i,
                title=f"Issue {100 + i}",
                body=f"Body {i}",
                labels=[TODO_LABEL],
            )
            self.story_service.check_for_update(issue)

        all_stories = self.story_storage.get_all()
        assert len(all_stories) == 5

        for i in range(5):
            story = self.story_storage.get_story(100 + i)
            assert story is not None
            assert story.number == 100 + i


if __name__ == "__main__":
    unittest.main()
