import json
import unittest

from tests.helper.assert_helper import assert_as_jsons
from tests.helper.telegram_helper import generate_command_message, generate_message


class TestTelegramHelper(unittest.TestCase):
    def test_generate_message(self):
        text = "Hello"
        from_id = 123
        message = generate_message(text, from_id)

        # then
        expected = json.loads(
            '{"message": {"chat": {"first_name": "Test", "id": 39622980, "last_name": "Test Lastname", "type": "private", "username": "Test"}, "date": 1441645532, "from": {"first_name": "Test", "id": 123, "is_bot": false, "last_name": "Test Lastname", "username": "Test"}, "message_id": 1365, "text": "Hello"}, "update_id": 10000}'
        )
        assert_as_jsons(expected, message)

    def test_generate_message_with_file(self):
        text = "Hello"
        from_id = 123
        message = generate_message(text, from_id, "test.csv")

        # then
        expected = json.loads(
            '{"update_id": 10000, "message": {"date": 1441645532, "chat": {"type": "private", "last_name": "Test Lastname", "id": 39622980, "first_name": "Test", "username": "Test"}, "message_id": 1365, "from": {"last_name": "Test Lastname", "id": 123, "first_name": "Test", "username": "Test", "is_bot": false}, "text": "Hello", "document": {"file_name": "test.csv", "file_id": "BQACAgIAAxkBAAOOZ8c7YDE5VprtY5BjSD25yVMGzxMAAoBwAALuYzhKRt3fKIEsjI42BA", "file_size": 12260, "file_unique_id": "AgADgHAAAu5jOEo", "mime_type": "text/csv"}}}'
        )
        assert_as_jsons(expected, message)

    def test_generate_command_message(self):
        text = "/start"
        from_id = 123
        message = generate_command_message(text, from_id)
        expected = json.loads(
            '{"message": {"channel_chat_created": false, "chat": {"first_name": "Mota", "id": 396229808, "last_name": "Cota", "type": "private", "username": "motacota"}, "date": 1738772945, "delete_chat_photo": false, "entities": [{"length": 6, "offset": 0, "type": "bot_command"}], "from": {"first_name": "Mota", "id": 123, "is_bot": false, "language_code": "ru", "last_name": "Cota", "username": "motacota"}, "group_chat_created": false, "message_id": 135, "supergroup_chat_created": false, "text": "/start"}, "update_id": 620597391}'
        )
        assert_as_jsons(expected, message)


if __name__ == "__main__":
    unittest.main()
