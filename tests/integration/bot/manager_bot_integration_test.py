import unittest

from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
    get_actual_user_prompt,
    get_actual_system_prompt,
)
from src.infrastructure.telegram.telegram_api import get_messages_sent
from src.ioc import storage
from tests.helper.assert_helper import assert_equals, assert_equals_not_strict, assert_as_jsons
from tests.helper.db_helper import mock_user
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.file_helper import get_file_content
from tests.helper.telegram_helper import generate_command_message


class BotIntegrationTest(unittest.TestCase):
    def test_manager_bot_welcome_message(self):
        # given
        prepare_new_test_env()

        # when
        payload = generate_command_message("/start", 396229808)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals(
            get_file_content("files/expected_welcome_message.txt"), get_messages_sent()[0]
        )

    def test_configure_behaviour(self):
        # given
        prepare_new_test_env()
        set_predefined_llm_response("Hello kitty")
        mock_user("396229111", "admin")

        # when
        payload = generate_command_message("/create like a fish", 396229111)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Bot is created. Follow @test_example_bot_link", get_messages_sent()[0])

        assert_equals_not_strict(
            get_file_content("files/expected_behavior_prompt.txt"),
            get_actual_system_prompt(),
        )
        assert_equals("like a fish", get_actual_user_prompt())

    def test_grant_by_invalid_identifier(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")

        # when
        payload = generate_command_message("/grant yolo rnp", 396229222)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals(
            "Invalid telegram ID or link. Telegram link must start with @ or t.me/. Telegram ID must be a number.",
            get_messages_sent()[0],
        )

    def test_grant_not_existing_user_by_link(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")

        # when
        payload = generate_command_message("/grant @yolo rnp", 396229222)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("User @yolo authorized successfully to rnp", get_messages_sent()[0])

        actual_user = storage.find_user_by_telegram_link("yolo")
        assert_as_jsons("files/expected_user_with_link.json", actual_user)

    def test_revoke_not_existing_user(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")

        # when
        payload = generate_command_message("/revoke @yolo rnp", 396229222)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("User already doesn't have access to rnp", get_messages_sent()[0])

        actual_user = storage.find_user_by_telegram_link("yolo")
        assert_as_jsons("files/expected_new_revoked_user.json", actual_user)

    def test_revoke_by_link(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")
        mock_user("123123123", "rnp")

        # when
        payload = generate_command_message("/revoke @yolo rnp", 396229222)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("User already doesn't have access to rnp", get_messages_sent()[0])

        actual_user = storage.find_user_by_telegram_link("yolo")
        assert_as_jsons("files/expected_revoked_user.json", actual_user)

    def test_grant_not_existing_user_by_id(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")

        # when
        payload = generate_command_message("/grant 1231231 rnp", 396229222)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("User 1231231 authorized successfully to rnp", get_messages_sent()[0])

        actual_user = storage.find_user_by_telegram_id("1231231")
        assert_as_jsons("files/expected_user_with_id.json", actual_user)

    def test_list_users(self):
        # given
        prepare_new_test_env()
        mock_user("396229222", "admin")

        # when
        payload = generate_command_message("/list_users", 396229222)

        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals_not_strict(
            """Users and their roles:
               @None - admin, assistant, codewriter
               @None - admin, assistant, codewriter
               @motacota - admin""",
            get_messages_sent()[0],
        )


if __name__ == "__main__":
    unittest.main()
