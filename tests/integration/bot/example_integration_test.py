import unittest

from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
    get_actual_user_prompt,
    get_actual_system_prompt,
)
from src.infrastructure.telegram.telegram_api import get_messages_sent
from tests.helper.assert_helper import assert_equals
from tests.helper.db_helper import mock_user
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.telegram_helper import generate_message


class BotIntegrationTest(unittest.TestCase):

    def test_example_echo_admin(self):
        # given
        prepare_new_test_env()
        mock_user("1111111", "assistant")
        set_predefined_llm_response("Hello admin user for example")

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/example", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Hello admin user for example", get_messages_sent()[0])

    def test_example_echo(self):
        # given
        prepare_new_test_env()
        mock_user("1111111", "assistant")
        set_predefined_llm_response("Hello assistant user for example")

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/example", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Hello assistant user for example", get_messages_sent()[0])
        assert_equals("I'm assistant example bot", get_actual_system_prompt())
        assert_equals("/start", get_actual_user_prompt())

    def test_example_echo_error_response(self):
        # given
        prepare_new_test_env()
        mock_user("1111111", "assistant")
        ## LLM mock will throw an exception because no response mocked.

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/example", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("An error occurred.", get_messages_sent()[0])


if __name__ == "__main__":
    unittest.main()
