import unittest

from src.app.service.entities import UserContext
from src.app.service.entities import UserFile
from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
)
from src.infrastructure.telegram.telegram_api import get_messages_sent
from src.ioc import storage
from tests.helper.assert_helper import assert_equals, assert_as_jsons
from tests.helper.db_helper import mock_user
from tests.helper.environemnt_helper import prepare_new_test_env, webhook_client
from tests.helper.file_helper import get_file_content
from tests.helper.telegram_helper import generate_command_message, generate_message


class RnpBotIntegrationTest(unittest.TestCase):
    def setUp(self):
        """Prepare fresh test environment before each test"""
        prepare_new_test_env()

    def test_files_command_with_no_files(self):
        # given
        mock_user("396229808", "rnp")

        # when
        payload = generate_command_message("/files", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals(get_file_content("files/expected_default_files.txt"), get_messages_sent()[0])

    def test_files_command_with_files(self):
        # given

        files = [
            UserFile(
                original_filename="report.pdf",
                original_url="https://example.com/report.pdf",
                size=0,
                path="fakepath",
            ),
            UserFile(
                original_filename="data.csv",
                original_url="https://example.com/data.csv",
                size=0,
                path="fakepath",
            ),
        ]
        mock_user("396229808", "rnp", files=files)

        # when
        payload = generate_command_message("/files", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        response = get_messages_sent()[0]
        expected = get_file_content("files/expected_user_files.txt")
        assert_equals(expected, response)

    def test_start_command(self):
        # given
        mock_user("396229808", "rnp")

        # when
        payload = generate_command_message("/start", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        response = get_messages_sent()[0]
        expected = """Available commands:
/files - List your uploaded files
/add <url> - Add a file by URL
/delete <filename> - Delete a file
/select <filename> - Select a file for analysis

To upload a file, simply send any .csv file without any text message."""
        assert_equals(expected, response)

    def test_rnp_echo(self):
        # given
        prepare_new_test_env()
        mock_user("1111111", "rnp")
        set_predefined_llm_response("Hello admin user for example")

        # when
        payload = generate_message("/start", 1111111)
        actualResponse = webhook_client.post("/webhook/rnp", json=payload)

        # then
        ## TODO assert the user is inserted
        assert_equals(200, actualResponse.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Mocked business analyst response", get_messages_sent()[0])

    def test_add_command_success(self):
        # given
        mock_user("396229808", "rnp")

        # when
        payload = generate_command_message(f"/add https://example.com/report.pdf", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals(
            f"File 'report.pdf' added successfully with URL: https://example.com/report.pdf",
            get_messages_sent()[0],
        )
        user = storage.find_user_by_telegram_id("396229808")
        added_file = user.files[0]
        assert added_file.original_url == "https://example.com/report.pdf"
        assert added_file.original_filename == "report.pdf"
        assert added_file.size == 3000

    def test_delete_command(self):
        # given
        files = [
            UserFile(
                original_filename="report.pdf",
                original_url="https://example.com/report.pdf",
                size=0,
                path="fakepath",
            ),
            UserFile(
                original_filename="data.csv",
                original_url="https://example.com/data.csv",
                size=0,
                path="fakepath",
            ),
        ]
        mock_user("396229808", "rnp", files=files)

        # when
        payload = generate_command_message(f"/delete report.pdf", 396229808)
        webhook_client.post("/webhook/rnp", json=payload)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(2, len(get_messages_sent()))
        assert_equals(f"File 'report.pdf' deleted successfully", get_messages_sent()[0])
        expected = get_file_content("files/expected_user_after_deletion.json")
        assert_as_jsons(expected, storage.find_user_by_telegram_id("396229808"))

    def test_add_command_missing_argument(self):
        # given
        mock_user("396229808", "rnp")

        # when
        payload = generate_command_message("/add", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Please provide a file URL. Usage: /add <file_url>", get_messages_sent()[0])

    def test_select_command(self):
        # given
        files = [
            UserFile(
                original_filename="report.pdf",
                original_url="https://example.com/report.pdf",
                size=0,
                path="fakepath",
            ),
            UserFile(
                original_filename="data.csv",
                original_url="https://example.com/data.csv",
                size=0,
                path="fakepath",
            ),
        ]
        # Create user with initial current file set to report.pdf
        mock_user("396229808", "rnp", files=files, context=UserContext(current_file="report.pdf"))

        # when
        payload = generate_command_message("/select data.csv", 396229808)
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals("Selected file 'data.csv' as current file", get_messages_sent()[0])

        # Verify user's current file was updated
        user = storage.find_user_by_telegram_id("396229808")
        assert_equals("data.csv", user.context.current_file)

    def test_file_upload(self):
        # given
        mock_user("396229808", "rnp")

        # when
        payload = generate_message(None, 396229808, file="test_data.csv")
        actual_response = webhook_client.post("/webhook/rnp", json=payload)

        # then
        assert_equals(200, actual_response.status_code)
        assert_equals(1, len(get_messages_sent()))
        assert_equals(f"File 'test_data.csv' added successfully", get_messages_sent()[0])

        # Verify file was added to user
        user = storage.find_user_by_telegram_id("396229808")
        assert_equals(1, len(user.files))
        assert_as_jsons("files/expected_uploaded_file.json", user.files)


if __name__ == "__main__":
    unittest.main()
