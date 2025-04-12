import unittest

from src.infrastructure.telegram.telegram_api import get_messages_sent
from tests.helper.assert_helper import assert_equals
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.telegram_helper import generate_message, generate_command_message


class BotIntegrationTest(unittest.TestCase):
    def test_example_echo_not_authorized(self):
        # given
        prepare_new_test_env()

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/example", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Not authorized.", get_messages_sent()[0])

    def test_rnp_echo_not_authorized(self):
        # given
        prepare_new_test_env()

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/rnp", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Not authorized.", get_messages_sent()[0])

    def test_configure_behaviour_not_authorized(self):
        # given
        prepare_new_test_env()

        # when
        payload = generate_command_message("/create like a fish", 1111111)
        actualResponse = webhook_client.post("/webhook/manager", json=payload)

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Not authorized.", get_messages_sent()[0])


if __name__ == "__main__":
    unittest.main()
