from tests.helper.file_helper import get_json


def generate_message(text: str = None, from_id: int = 123456789, file: str = None):
    """
    Generate a basic Telegram message with fixed fields.

    :param text: The text of the message (optional, if None the text field will be removed).
    :param from_id: The ID of the sender.
    :return: A dictionary representing the Telegram message.
    """
    text_message = get_json("files/text_message_template.json")
    if text is not None:
        text_message["message"]["text"] = text
    else:
        text_message["message"].pop("text", None)
    text_message["message"]["from"]["id"] = from_id

    if file:
        text_message["message"]["document"] = {}
        text_message["message"]["document"]["file_name"] = file
        text_message["message"]["document"][
            "file_id"
        ] = "BQACAgIAAxkBAAOOZ8c7YDE5VprtY5BjSD25yVMGzxMAAoBwAALuYzhKRt3fKIEsjI42BA"
        text_message["message"]["document"]["file_size"] = 12260
        text_message["message"]["document"]["file_unique_id"] = "AgADgHAAAu5jOEo"
        text_message["message"]["document"]["mime_type"] = "text/csv"
    return text_message


def generate_command_message(text: str, from_id: int = 123456789):
    """
    Generate a basic Telegram message with fixed fields.

    :param text: The text of the message.
    :param from_id: The ID of the sender.
    :return: A dictionary representing the Telegram message.
    """
    """
    Generate a basic Telegram message with fixed fields.

    :param text: The text of the message.
    :param from_id: The ID of the sender.
    :return: A dictionary representing the Telegram message.
    """
    text_message = get_json("files/command_message_template.json")
    text_message["message"]["text"] = text
    text_message["message"]["entities"][0]["length"] = (
        len(text) if text.find(" ") == -1 else text.find(" ")
    )
    text_message["message"]["from"]["id"] = from_id
    return text_message
