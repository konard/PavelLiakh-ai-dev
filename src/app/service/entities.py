from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserFile:
    original_filename: str
    original_url: Optional[str]  # Original URL of the file.
    size: int  # File size in bytes
    path: str  # Internal file path


DEFAULT_FILENAME = "default"


@dataclass
class UserContext:
    current_file: Optional[str] = None  # Current file name.


ROLE_ADMIN = "admin"
ROLE_CODEWRITER = "codewriter"
ROLE_RNP = "rnp"
ROLE_ASSISTANT = "assistant"


@dataclass
class User:
    telegram_id: Optional[str] = None  # Unique identifier for the user from Telegram
    _id: str = None  # DB ID - will be populated by MongoDB
    telegram_name: Optional[str] = None  # The user's Telegram username
    telegram_link: Optional[str] = None  # Link to user's Telegram profile
    roles: List[str] = field(default_factory=list)  # List of roles assigned to the user
    files: List[UserFile] = field(default_factory=list)  # List of files uploaded by the user
    context: Optional[UserContext] = None  # User context for the current session


@dataclass
class Bot:
    owner_id: str  # User ID of the bot owner
    token: str  # Telegram bot token for API interactions
    link: str  # Name of the bot
    _id: Optional[str] = None  # DB ID - will be populated by MongoDB
    is_manager: Optional[bool] = False  # Whether the bot is the manager bot
    is_example: Optional[bool] = False  # Whether the bot is the example bot
    behaviour: str = "I'm assistant bot"  # Default bot behaviour


@dataclass
class ErrorLog:
    user_id: str  # User ID related to the error
    message: str  # Original message that caused the error
    timestamp: str  # Timestamp of the error occurrence
    error: str  # Detailed error message or stacktrace
    _id: str = None  # DB ID - will be populated by MongoDB


NOT_AUTHORIZED_RESPONSE = "Not authorized."
ERROR_RESPONSE = "An error occurred."


@dataclass
class ConversationMessage:
    telegram_user_id: str  # Telegram user ID
    text: str  # Message text content
    message_id: Optional[str]  # Telegram message ID
    chat_id: Optional[str]  # Telegram chat ID
    timestamp: str
    user_id: Optional[str]  # User ID related to the message
    _id: Optional[str] = None  # DB ID - will be populated by MongoDB
    telegram_user_name: Optional[str] = None  # The user's Telegram username
    telegram_user_link: Optional[str] = None  # Link to user's Telegram profile
    bot_link: Optional[str] = None  # Link to the bot that received the message
    response: Optional[str] = None  # Bot's response to the message
