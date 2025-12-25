import unittest
from unittest.mock import Mock

from src.app.domain.story import Story, NEW_STATE, PLANNING_STATE
from src.app.service.planner_service import PlannerService, Plan
from src.app.service.code_request_service import CodeRequestService, CodeFiles
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.db.story_storage import StoryStorage
from tests.helper.db_helper import reset_storage


class TestDevelopmentWorkflowIntegration(unittest.TestCase):
    """Integration tests for planning and code generation workflow"""

    def setUp(self):
        reset_storage()
        self.log = Mock()
        self.storage = JsonStorage()
        self.story_storage = StoryStorage(self.storage, self.log)
        self.llm_client = Mock()

        self.planner_service = PlannerService(
            self.llm_client, self.story_storage, self.log
        )
        self.code_request_service = CodeRequestService(
            self.llm_client, self.story_storage, self.log
        )

    def tearDown(self):
        reset_storage()

    def test_plan_and_implement_workflow(self):
        story = Story(
            number=1,
            name="Add feature X",
            description="Implement feature X",
            state=NEW_STATE,
        )

        saved_story = self.story_storage.save_story(story)

        mock_plan = Plan(plan=["Create module.py", "Add tests"])
        self.llm_client.generate_response.return_value = mock_plan

        plan_result = self.planner_service.plan(saved_story)

        assert plan_result.plan == ["Create module.py", "Add tests"]
        assert saved_story.state == PLANNING_STATE
        assert saved_story.build_plan == ["Create module.py", "Add tests"]

        retrieved_story = self.story_storage.get_story(1)
        assert retrieved_story.build_plan == ["Create module.py", "Add tests"]

        mock_code = CodeFiles(
            files={"module.py": "def func(): pass", "test_module.py": "def test(): pass"}
        )
        self.llm_client.generate_response.return_value = mock_code

        code_result = self.code_request_service.implement(retrieved_story)

        assert "module.py" in code_result
        assert "test_module.py" in code_result
        assert retrieved_story.code_files == code_result

        final_story = self.story_storage.get_story(1)
        assert final_story.code_files is not None
        assert len(final_story.code_files) == 2

    def test_story_state_progression(self):
        story = Story(number=2, name="Test story", state=NEW_STATE)
        self.story_storage.save_story(story)

        assert story.state == NEW_STATE

        mock_plan = Plan(plan=["Step 1"])
        self.llm_client.generate_response.return_value = mock_plan
        self.planner_service.plan(story)

        assert story.state == PLANNING_STATE

        retrieved = self.story_storage.get_story(2)
        assert retrieved.state == PLANNING_STATE

    def test_plan_persistence_across_services(self):
        story = Story(number=3, name="Persistence test", state=NEW_STATE)
        self.story_storage.save_story(story)

        mock_plan = Plan(plan=["First step", "Second step"])
        self.llm_client.generate_response.return_value = mock_plan

        self.planner_service.plan(story)

        fresh_story = self.story_storage.get_story(3)
        assert fresh_story.build_plan == ["First step", "Second step"]

        mock_code = CodeFiles(files={"output.py": "code"})
        self.llm_client.generate_response.return_value = mock_code

        self.code_request_service.implement(fresh_story)

        final_story = self.story_storage.get_story(3)
        assert final_story.build_plan == ["First step", "Second step"]
        assert final_story.code_files == {"output.py": "code"}


if __name__ == "__main__":
    unittest.main()
