from src.app.service.entities import (
    ROLE_ADMIN,
    ROLE_ASSISTANT,
    ConversationMessage,
    User,
    NOT_AUTHORIZED_RESPONSE,
    ERROR_RESPONSE,
)
from src.config import config
from src.infrastructure.logger import get_logger
from src.infrastructure.telegram.telegram_api import reply_to_telegram
from src.ioc import conversation_service, error_service, bot_service, llm_client

log = get_logger(__name__)


class ResponseGenerator:

    def handle_message(self, message: ConversationMessage, user: User) -> str:
        try:
            bot = bot_service.find_bot_for_message(message)

            is_authorized = (ROLE_ADMIN in user.roles) or (ROLE_ASSISTANT in user.roles)
            if not is_authorized:
                return NOT_AUTHORIZED_RESPONSE

            response = llm_client.generate_response(bot.behaviour, message.text)

            return response
        except Exception as e:
            error_service.log_error(user_id=message.telegram_user_id, message=message.text, error=e)
            return ERROR_RESPONSE


# Create default instance for backward compatibility
default_generator = ResponseGenerator()


async def echo(update, context):
    """Echo the user message."""
    log.info("Received message from user %s", update.effective_user.id)
    message = conversation_service.build(update, config.example_bot_link)
    user = conversation_service.users_service.get_or_create_user_by_message(message)

    response = default_generator.handle_message(message, user)
    message.response = response
    conversation_service.save(message)

    log.info("Responding to user %s with: %s", update.effective_user.id, message.response)
    await reply_to_telegram(update, message.response)
