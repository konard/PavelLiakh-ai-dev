import unittest

from src.infrastructure.telegram.telegram_api import get_messages_sent, reset_mock
from tests.helper.assert_helper import assert_equals
from tests.helper.db_helper import mock_user
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.telegram_helper import generate_command_message, generate_message


class UserWorkflowTest(unittest.TestCase):
    def test_new_user_can_access_rnp(self):
        # given
        prepare_new_test_env()
        reset_mock()
        mock_user("396229222", "admin")  # Admin user

        # when
        webhook_client.post(
            "/webhook/manager", json=generate_command_message("/grant 123456789 rnp", 396229222)
        )
        webhook_client.post("/webhook/rnp", json=generate_message("Test question", 123456789))

        # then
        messages = get_messages_sent()
        assert_equals(2, len(messages))
        assert_equals("Mocked business analyst response", messages[1])


if __name__ == "__main__":
    unittest.main()
