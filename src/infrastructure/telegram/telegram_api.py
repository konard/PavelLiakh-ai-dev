"""
This one is a wrapper for telegram response for testing purposes.
"""

from src.infrastructure.logger import get_logger

log = get_logger(__name__)
from src.config import config

# list of messages to be sent to telegram mocked
messages_sent = []

# This is the maximum length of message that can be sent to telegram.
# I found no mentions in documentation, so here is latest reference where I found it: https://stackoverflow.com/questions/55672791/how-to-extend-the-limit-for-reply-from-telegram-bot-and-what-is-the-limit-of-rep
MAXIMUM_MESSAGE_LENGTH = 4096

# This is limitation on how many parts of one message may be sent at once.
# I've selected value 5 without any referenec - just by feeling, so feel free to adjust the value based on objective data e.g. docs or proof of concept testing.
MAXIMUM_MESSAGE_PER_BATCH = 5


def reset_mock():
    """Reset the messages sent."""
    global messages_sent
    messages_sent = []


def get_messages_sent():
    """Get the messages sent."""
    global messages_sent
    return messages_sent


async def reply_to_telegram(update, response: str):
    # FIXME must SPLIT message into parts if it out of size limit
    """Reply to telegram and return the response."""
    global messages_sent

    if not response:
        raise RuntimeError("Telegram message must not be empty")

    if len(response) == 0:
        raise RuntimeError("Telegram message must contain at least one character")

    if config.is_test():
        log.info(f"TEST Environment: mocked message sent {response}")
        messages_sent.append(response)
        return

    log.info(f"Sending message to telegram: {response}")
    await update.message.reply_text(response)
