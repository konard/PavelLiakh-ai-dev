from src.app.service.entities import ROLE_ADMIN, ConversationMessage, NOT_AUTHORIZED_RESPONSE
from src.config import config
from src.infrastructure.logger import get_logger
from src.infrastructure.telegram.telegram_api import reply_to_telegram
from src.ioc import (
    storage,
    conversation_service,
    users_service,
    bot_service,
)

log = get_logger(__name__)

HELP_MESSAGE = """Welcome to Manager Bot! Here's what you can do:

/create <behavior> - Update example bot's behavior
/grant <telegram_link> - Grant user access to use assistant
/revoke <telegram_link> - Revoke user access to use assistant
/list_users - List all users and their roles (admin only)
Send any message - Get a response from the manager bot

Example usage:
/create Be more friendly and helpful
/grant @username
/revoke @username
/list_users
"""


def build_message(update) -> ConversationMessage:
    """Build a message object from the update"""
    return conversation_service.build(update, config.manager_bot_link)


async def check_authorization(update, message: ConversationMessage) -> bool:
    """Check if user has the required role"""
    user = users_service.get_or_create_user_by_message(message)
    is_authorized = ROLE_ADMIN in user.roles
    if not is_authorized:
        message.response = NOT_AUTHORIZED_RESPONSE
        conversation_service.save(message)
        await reply_to_telegram(update, NOT_AUTHORIZED_RESPONSE)
    return is_authorized


async def start(update, context):
    """Send welcome message with help instructions"""
    log.info("Received /start from %s", update.effective_user.first_name)
    await reply_to_telegram(update, HELP_MESSAGE)


async def list_users(update, context):
    """List all users and their roles (admin only)"""
    log.info("Received /list command from %s", update.effective_user.first_name)

    # Check if user is admin
    message = build_message(update)
    if not await check_authorization(update, message):
        return

    # Get all users from storage
    users = storage.get_all_users()
    if not users:
        await reply_to_telegram(update, "No users found")
        return

    # Format user list with roles
    user_list = []
    for user in users:
        roles = ", ".join(user.roles) if user.roles else "no roles"
        user_list.append(f"@{user.telegram_link} - {roles}")

    response = "Users and their roles:\n\n" + "\n".join(user_list)
    await reply_to_telegram(update, response)


async def revoke(update, context):
    """Revoke user access to use assistant"""
    log.info(
        "Received /revoke command from %s: %s",
        update.effective_user.first_name,
        update.message.text,
    )

    # Check if user is admin
    message = build_message(update)
    if not await check_authorization(update, message):
        return

    # Get the telegram link from the message
    parts = update.message.text.split(maxsplit=2)  # Split into at most 3 parts

    if len(parts) < 3:  # Must have /revoke, username, and role
        await reply_to_telegram(update, "Usage: /revoke <username> <role>")
        return

    _, username, role = parts  # Unpack values, ignoring /revoke

    # Revoke user access
    message.response = await users_service.revoke_user_access(username, role)
    conversation_service.save(message)
    await reply_to_telegram(update, message.response)


async def grant(update, context):
    """Grant user access to use assistant"""
    log.info(
        "Received /grant command from %s: %s", update.effective_user.first_name, update.message.text
    )

    # Check if user is admin
    message = build_message(update)
    if not await check_authorization(update, message):
        return

    # Get the telegram link from the message
    parts = update.message.text.split(maxsplit=2)  # Split into at most 3 parts

    if len(parts) < 3:  # Must have /revoke, username, and role
        await reply_to_telegram(update, "Usage: /grant <username> <role>")
        return

    _, username, role = parts  # Unpack values, ignoring /revoke

    # Grant user access
    message.response = await users_service.grant_user_access(username, role)
    conversation_service.save(message)
    await reply_to_telegram(update, message.response)


async def create(update, context):
    """Update example bot's behavior"""
    log.info("Received /create command from %s", update.effective_user.first_name)

    # Check if user is admin
    message = build_message(update)
    if not await check_authorization(update, message):
        return

    # Get the behavior text from the message
    behavior = update.message.text.replace("/create", "").strip()
    if not behavior:
        await reply_to_telegram(update, "Please provide a behavior description after /create")
        return

    # Update example bot's behavior
    message.response = bot_service.update_example_bot_behavior(behavior)
    conversation_service.save(message)
    await reply_to_telegram(update, message.response)
