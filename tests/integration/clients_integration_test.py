import unittest

from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.db_helper import reset_storage
from tests.helper.assert_helper import assert_equals, assert_as_jsons
from src.ioc import client_service, sku_service
from src.app.mp.mp_entities import Sku
from src.app.domain.client import Client


class RegisterEndpointIntegrationTest(unittest.TestCase):
    def setUp(self):
        """Prepare fresh test environment before each test"""
        prepare_new_test_env()
        reset_storage()

    def test_register_new_client_success(self):
        # given - create test SKU
        # given - create test SKU
        prepare_new_test_env()
        test_sku = Sku(number="TEST123", category="Test")
        sku_service.process_file = lambda _: sku_service.storage.save(test_sku)

        request_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "article_number": "TEST123"
        }

        # when
        response = webhook_client.post(
            "/register",
            json=request_data
        )

        # then
        assert_equals(200, response.status_code)
        assert_equals("success", response.json()["status"])
        
        clients = client_service.get_all_clients()
        assert_equals(1, len(clients))
        assert_as_jsons("files/expected_clients.json", clients[0])

if __name__ == "__main__":
    unittest.main()
