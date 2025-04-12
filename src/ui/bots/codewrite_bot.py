from src.app.service.entities import ROLE_CODEWRITER
from src.config import config
from src.infrastructure.logger import get_logger
from src.ioc import conversation_service
from src.infrastructure.telegram.telegram_api import reply_to_telegram

log = get_logger(__name__)


async def process_codewriting(update, context):
    message = conversation_service.build(update, config.manager_bot_link)
    log.info(f"Received message from user {message.telegram_user_id}: {message.text}")

    user = conversation_service.users_service.get_or_create_user_by_message(message)
    is_authorized = ROLE_CODEWRITER in user.roles
    if not is_authorized:
        log.info(f"User {message.telegram_user_id} is not authorized to use codewriting bot")
        message.response = "You are not authorized to use this bot"
        await reply_to_telegram(update, message.response)
        return

    # Disabled because of infinite loop in production
    await reply_to_telegram(update, "Code generation is disabled for now")
