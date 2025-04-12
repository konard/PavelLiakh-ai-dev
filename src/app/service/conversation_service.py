from src.app.service.users_service import UsersService
from src.infrastructure.db.json_storage import MongoStorage
from src.app.service.entities import ConversationMessage


class ConversationService:
    def __init__(self, storage: MongoStorage, log, users_service: UsersService):
        self.users_service = users_service
        self.storage = storage
        self.log = log

    def build(self, update, bot_link: str) -> ConversationMessage:
        """Build a conversation message from the update"""
        message = ConversationMessage(
            telegram_user_id=str(update.effective_user.id),
            text=update.message.text,
            timestamp=update.message.date.isoformat(),
            user_id=None,
            message_id=update.message.message_id,
            chat_id=update.message.chat_id,
            telegram_user_name=update.effective_user.full_name,
            telegram_user_link=update.effective_user.username,
            bot_link=bot_link,
        )
        user = self.users_service.get_or_create_user_by_message(message)
        message.user_id = user._id
        return message

    def save(self, message: ConversationMessage) -> None:
        """Save conversation data including user information"""
        self.users_service.get_or_create_user_by_message(message)
        self.storage.save_conversation(message)
        self.log.debug(f"Saved conversation data for user {message.telegram_user_id}")
