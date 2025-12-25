import unittest
from unittest.mock import Mock

from src.app.domain.story import Story, NEW_STATE, PLANNING_STATE
from src.app.service.planner_service import PlannerService, Plan


class TestPlannerService(unittest.TestCase):
    def setUp(self):
        self.llm_client = Mock()
        self.story_storage = Mock()
        self.log = Mock()
        self.service = PlannerService(self.llm_client, self.story_storage, self.log)

    def test_plan_updates_story_state(self):
        story = Story(number=1, name="Test Story", description="Test description", state=NEW_STATE)

        mock_plan = Plan(plan=["Step 1", "Step 2", "Step 3"])
        self.llm_client.generate_response.return_value = mock_plan

        result = self.service.plan(story)

        assert story.state == PLANNING_STATE
        assert result == mock_plan

    def test_plan_calls_llm_with_correct_prompts(self):
        story = Story(
            number=1,
            name="Implement feature X",
            description="Add feature X to the system",
            state=NEW_STATE,
        )

        mock_plan = Plan(plan=["Step 1", "Step 2"])
        self.llm_client.generate_response.return_value = mock_plan

        self.service.plan(story)

        self.llm_client.generate_response.assert_called_once()
        call_args = self.llm_client.generate_response.call_args
        system_prompt = call_args[0][0]
        user_request = call_args[0][1]
        output_format = call_args[0][2]

        assert "Technical planner" in system_prompt
        assert "Implement feature X" in user_request
        assert "Add feature X to the system" in user_request
        assert output_format == Plan

    def test_plan_saves_generated_plan_to_story(self):
        story = Story(number=1, name="Test", description="Test", state=NEW_STATE)

        mock_plan = Plan(plan=["Create file x.py", "Modify file y.py"])
        self.llm_client.generate_response.return_value = mock_plan

        self.service.plan(story)

        assert story.build_plan == ["Create file x.py", "Modify file y.py"]
        self.story_storage.save_story.assert_called_once_with(story)

    def test_plan_returns_plan_object(self):
        story = Story(number=1, name="Test", description="Test", state=NEW_STATE)

        expected_plan = Plan(plan=["Step A", "Step B", "Step C"])
        self.llm_client.generate_response.return_value = expected_plan

        result = self.service.plan(story)

        assert result == expected_plan
        assert isinstance(result, Plan)


if __name__ == "__main__":
    unittest.main()
