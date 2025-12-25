import unittest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel

from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ai import llm_client_mock


class MockResponse(BaseModel):
    result: str


class TestLlmClient(unittest.TestCase):
    def setUp(self):
        self.log = Mock()

    @patch("src.infrastructure.ai.llm_client.config")
    def test_init_sets_model(self, mock_config):
        mock_config.openai_api_key = "test-key"
        mock_config.is_test.return_value = False

        client = LlmClient(self.log, model="gpt-4o-mini")

        assert client.model == "gpt-4o-mini"
        assert client.log == self.log

    @patch("src.infrastructure.ai.llm_client.config")
    def test_generate_response_in_test_mode_returns_mock(self, mock_config):
        mock_config.is_test.return_value = True
        mock_config.openai_api_key = "test-key"
        llm_client_mock.set_predefined_llm_response("Mocked response")

        client = LlmClient(self.log)

        result = client.generate_response(
            "System prompt", "User prompt", output_format=None
        )

        assert result == "Mocked response"

    @patch("src.infrastructure.ai.llm_client.config")
    @patch("src.infrastructure.ai.llm_client.client")
    def test_generate_response_with_output_format(self, mock_openai_client, mock_config):
        mock_config.is_test.return_value = False
        mock_config.openai_api_key = "test-key"

        mock_response = MockResponse(result="Test result")
        mock_openai_client.chat.completions.create.return_value = mock_response

        client = LlmClient(self.log, model="gpt-4o-mini")
        result = client.generate_response(
            "System", "User", output_format=MockResponse
        )

        assert result == mock_response
        mock_openai_client.chat.completions.create.assert_called_once()

    @patch("src.infrastructure.ai.llm_client.config")
    @patch("src.infrastructure.ai.llm_client.client")
    def test_generate_response_without_output_format(self, mock_openai_client, mock_config):
        mock_config.is_test.return_value = False
        mock_config.openai_api_key = "test-key"

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_openai_client.chat.completions.create.return_value = mock_response

        client = LlmClient(self.log)
        result = client.generate_response("System", "User", output_format=None)

        assert result == "Generated text"

    @patch("src.infrastructure.ai.llm_client.config")
    def test_generate_reasoned_response_in_test_mode(self, mock_config):
        mock_config.is_test.return_value = True
        mock_config.openai_api_key = "test-key"
        llm_client_mock.set_predefined_llm_response("Reasoned response")

        client = LlmClient(self.log)
        result = client.generate_reasoned_response(
            system_prompt="Context", user_prompt="Question"
        )

        assert result == "Reasoned response"

    @patch("src.infrastructure.ai.llm_client.config")
    @patch("src.infrastructure.ai.llm_client.openai")
    def test_generate_reasoned_response_with_system_prompt(self, mock_openai, mock_config):
        mock_config.is_test.return_value = False
        mock_config.openai_api_key = "test-key"

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Reasoned answer"))]
        mock_openai.chat.completions.create.return_value = mock_response

        client = LlmClient(self.log)
        result = client.generate_reasoned_response(
            system_prompt="Context here", user_prompt="What is AI?"
        )

        assert result == "Reasoned answer"
        call_args = mock_openai.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert "Context here" in messages[0]["content"]
        assert "What is AI?" in messages[0]["content"]


if __name__ == "__main__":
    unittest.main()
