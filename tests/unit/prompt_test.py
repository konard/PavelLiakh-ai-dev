import unittest

from src.infrastructure.ai.prompt import Prompt
from tests.helper.assert_helper import assert_equals
from tests.helper.file_helper import get_file_content


class TestPrompt(unittest.TestCase):
    def test_to_str(self):
        prompt = Prompt(task="Test task", role="Object under test")
        assert_equals("Role: Object under test\n\nTask: Test task", prompt.to_str())

    def test_to_str_with_all_fields(self):
        prompt = Prompt(
            task="Complete task",
            role="Object under test",
            output="Expected output",
            instructions=["Follow these instructions", "Follow those instructions"],
            context=["Additional data 1", "Additional data 2"],
        )
        assert_equals(get_file_content("files/expected_prompt.txt"), prompt.to_str())


if __name__ == "__main__":
    unittest.main()
