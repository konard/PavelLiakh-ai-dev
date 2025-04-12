import unittest

from src.config import config
from tests.helper.assert_helper import assert_equals
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client


class ServiceApiIntegrationTest(unittest.TestCase):
    def test_version_api(self):
        # given
        prepare_new_test_env()
        config.version = "91a022b"

        # when
        actualResponse = webhook_client.get("/version")

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals("91a022b", actualResponse.json()["version"])

    def test_health_api(self):
        # given
        prepare_new_test_env()

        # when
        actualResponse = webhook_client.get("/health")

        # then
        assert_equals(200, actualResponse.status_code)
        assert_equals("ok", actualResponse.json()["status"])


if __name__ == "__main__":
    unittest.main()
