import unittest

from src.app.domain.story import (
    Story,
    NEW_STATE,
    PLANNING_STATE,
    DEVELOPMENT_STATE,
    DONE_STATE,
    CANCELLED_STATE,
    states,
)


class TestStory(unittest.TestCase):
    def test_story_creation_with_all_fields(self):
        story = Story(
            _id="1",
            number=123,
            name="Test Story",
            description="Test description",
            comments=["Comment 1", "Comment 2"],
            state=NEW_STATE,
            plan=["Step 1", "Step 2"],
            pr_link="https://github.com/test/test/pull/1",
            code_files={"file1.py": "content1", "file2.py": "content2"},
        )

        assert story._id == "1"
        assert story.number == 123
        assert story.name == "Test Story"
        assert story.description == "Test description"
        assert story.comments == ["Comment 1", "Comment 2"]
        assert story.state == NEW_STATE
        assert story.plan == ["Step 1", "Step 2"]
        assert story.pr_link == "https://github.com/test/test/pull/1"
        assert story.code_files == {"file1.py": "content1", "file2.py": "content2"}

    def test_story_creation_with_minimal_fields(self):
        story = Story()

        assert story._id is None
        assert story.number is None
        assert story.name is None
        assert story.description is None
        assert story.comments is None
        assert story.state is None
        assert story.plan is None
        assert story.pr_link is None
        assert story.code_files is None

    def test_story_states_constant(self):
        assert NEW_STATE == "NEW"
        assert PLANNING_STATE == "PLANNING"
        assert DEVELOPMENT_STATE == "DEVELOPMENT"
        assert DONE_STATE == "DONE"
        assert CANCELLED_STATE == "CANCELLED"

    def test_states_list_contains_all_states(self):
        assert NEW_STATE in states
        assert PLANNING_STATE in states
        assert DEVELOPMENT_STATE in states
        assert DONE_STATE in states
        assert CANCELLED_STATE in states
        assert len(states) == 5


if __name__ == "__main__":
    unittest.main()
