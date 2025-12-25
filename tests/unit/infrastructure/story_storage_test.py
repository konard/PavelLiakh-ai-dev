import unittest
from unittest.mock import Mock, MagicMock
from tinydb import Query

from src.app.domain.story import Story, NEW_STATE, PLANNING_STATE
from src.infrastructure.db.story_storage import StoryStorage


class TestStoryStorage(unittest.TestCase):
    def setUp(self):
        self.storage = Mock()
        self.log = Mock()
        self.story_db = Mock()
        self.storage.get_db.return_value = self.story_db

        self.story_storage = StoryStorage(self.storage, self.log)

    def test_init_gets_stories_db(self):
        self.storage.get_db.assert_called_once_with("stories")
        assert self.story_storage.story_db == self.story_db

    def test_get_story_calls_storage_find(self):
        expected_story = Story(number=123, name="Test Story")
        self.storage._find_entity.return_value = expected_story

        result = self.story_storage.get_story(123)

        assert result == expected_story
        self.storage._find_entity.assert_called_once()
        call_args = self.storage._find_entity.call_args
        assert call_args[1]["entity_class"] == Story

    def test_get_story_returns_none_when_not_found(self):
        self.storage._find_entity.return_value = None

        result = self.story_storage.get_story(999)

        assert result is None

    def test_save_story_calls_storage_save(self):
        story = Story(number=456, name="Save Test", state=NEW_STATE)
        saved_story = Story(number=456, name="Save Test", state=NEW_STATE)
        self.storage.save_entity.return_value = saved_story

        result = self.story_storage.save_story(story)

        assert result == saved_story
        self.storage.save_entity.assert_called_once()
        call_args = self.storage.save_entity.call_args
        assert call_args[1]["entity"] == story
        assert call_args[1]["entity_class"] == Story

    def test_get_all_returns_all_stories(self):
        self.story_db.all.return_value = [
            {"number": 1, "name": "Story 1", "state": NEW_STATE},
            {"number": 2, "name": "Story 2", "state": PLANNING_STATE},
        ]

        result = self.story_storage.get_all()

        assert len(result) == 2
        assert isinstance(result[0], Story)
        assert result[0].number == 1
        assert result[1].number == 2

    def test_get_all_returns_empty_list_when_no_stories(self):
        self.story_db.all.return_value = []

        result = self.story_storage.get_all()

        assert result == []

    def test_get_stories_by_state_filters_correctly(self):
        all_stories = [
            Story(number=1, name="Story 1", state=NEW_STATE),
            Story(number=2, name="Story 2", state=PLANNING_STATE),
            Story(number=3, name="Story 3", state=NEW_STATE),
        ]

        self.story_db.all.return_value = [
            {"number": 1, "name": "Story 1", "state": NEW_STATE},
            {"number": 2, "name": "Story 2", "state": PLANNING_STATE},
            {"number": 3, "name": "Story 3", "state": NEW_STATE},
        ]

        result = self.story_storage.get_stories_by_state(NEW_STATE)

        assert len(result) == 2
        assert all(story.state == NEW_STATE for story in result)

    def test_get_stories_by_state_returns_empty_when_no_match(self):
        self.story_db.all.return_value = [
            {"number": 1, "name": "Story 1", "state": NEW_STATE},
        ]

        result = self.story_storage.get_stories_by_state(PLANNING_STATE)

        assert result == []

    def test_get_stories_by_state_handles_none_state(self):
        self.story_db.all.return_value = [
            {"number": 1, "name": "Story 1", "state": None},
            {"number": 2, "name": "Story 2", "state": NEW_STATE},
        ]

        result = self.story_storage.get_stories_by_state(NEW_STATE)

        assert len(result) == 1
        assert result[0].number == 2


if __name__ == "__main__":
    unittest.main()
