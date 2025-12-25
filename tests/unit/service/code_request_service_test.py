import unittest
from unittest.mock import Mock

from src.app.domain.story import Story, PLANNING_STATE
from src.app.service.code_request_service import CodeRequestService, CodeFiles


class TestCodeRequestService(unittest.TestCase):
    def setUp(self):
        self.llm_client = Mock()
        self.story_storage = Mock()
        self.log = Mock()
        self.service = CodeRequestService(self.llm_client, self.story_storage, self.log)

    def test_implement_generates_code_files(self):
        story = Story(
            number=1,
            name="Test Story",
            description="Test description",
            state=PLANNING_STATE,
            build_plan=["Step 1", "Step 2"],
        )

        mock_response = CodeFiles(files={"file1.py": "content1", "file2.py": "content2"})
        self.llm_client.generate_response.return_value = mock_response

        result = self.service.implement(story)

        assert result == {"file1.py": "content1", "file2.py": "content2"}

    def test_implement_calls_llm_with_correct_prompts(self):
        story = Story(
            number=1,
            name="Implement feature",
            build_plan=["Create main.py", "Create utils.py"],
            state=PLANNING_STATE,
        )

        mock_response = CodeFiles(files={})
        self.llm_client.generate_response.return_value = mock_response

        self.service.implement(story)

        self.llm_client.generate_response.assert_called_once()
        call_args = self.llm_client.generate_response.call_args
        system_prompt = call_args[0][0]
        user_request = call_args[0][1]
        output_format = call_args[0][2]

        assert "Senior software engineer" in system_prompt
        assert "Implement feature" in user_request
        assert "Create main.py" in user_request
        assert "Create utils.py" in user_request
        assert output_format == CodeFiles

    def test_implement_saves_code_files_to_story(self):
        story = Story(
            number=1,
            name="Test",
            build_plan=["Step 1"],
            state=PLANNING_STATE,
        )

        generated_files = {"app.py": "def main(): pass", "test.py": "def test(): pass"}
        mock_response = CodeFiles(files=generated_files)
        self.llm_client.generate_response.return_value = mock_response

        self.service.implement(story)

        assert story.code_files == generated_files
        self.story_storage.save_story.assert_called_once_with(story)

    def test_implement_returns_code_files_dict(self):
        story = Story(number=1, name="Test", build_plan=["Step 1"], state=PLANNING_STATE)

        expected_files = {"main.py": "print('hello')"}
        mock_response = CodeFiles(files=expected_files)
        self.llm_client.generate_response.return_value = mock_response

        result = self.service.implement(story)

        assert result == expected_files
        assert isinstance(result, dict)


if __name__ == "__main__":
    unittest.main()
