from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application
from telegram import Update, User

from src.ui.bots.rnp_bot import (
    echo as rnp_echo,
    document as rnp_document,
    files as rnp_files,
    delete as rnp_delete,
    add as rnp_add,
    update as rnp_update,
    select as rnp_select,
    start as rnp_start,
)
from src.ui.bots.example_bot import echo as example_echo
from src.ui.bots.manager_bot import create, start, grant, revoke, list_users
from src.ui.bots.codewrite_bot import process_codewriting
from src.config import config
from src.infrastructure.logger import get_logger
import asyncio

log = get_logger(__name__)
MANAGER_BOT = None
EXAMPLE_BOT = None
RNP_BOT: Application = None


async def set_webhook(bot_app, webhook_url: str):
    """Set webhook URL for the bot"""
    if config.is_test() or config.is_dev():
        log.info("Skipping webhook setup in DEV/TEST environment: {webhook_url}")
        return
    with open(config.cert, "rb") as cert_file:
        result = await bot_app.set_webhook(webhook_url, certificate=cert_file)
    log.info(f"Webhook set for {webhook_url}. Success={result}")


def _init_bot(token: str, handlers: list, webhook_path: str):
    """Initialize a bot with given token and handlers for webhook"""
    log.info(f"Initializing bot with token: {token[:4]}...{token[-4:]}")
    bot_app = ApplicationBuilder().token(token).build()

    ip_address = config.ip_address
    webhook_host = f"https://{ip_address}:{config.port}"

    for handler in handlers:
        bot_app.add_handler(handler)
        log.debug(f"Added handler: {type(handler).__name__}")

    if config.is_test() or config.is_dev():
        # Do mock internal state of the bot to avoid real telegram API calling in test environment
        bot_app.bot._initialized = True
        mocked_bot = {
            "can_connect_to_business": False,
            "can_join_groups": True,
            "can_read_all_group_messages": False,
            "first_name": "Mocked Bot",
            "has_main_web_app": False,
            "id": 8094525394,
            "is_bot": True,
            "supports_inline_queries": False,
            "username": "mocked_bot_name",
        }
        bot_app.bot._bot_user = User.de_json(mocked_bot, bot_app.bot)
    else:
        asyncio.get_event_loop().run_until_complete(bot_app.bot.initialize())

    asyncio.get_event_loop().run_until_complete(bot_app.initialize())
    asyncio.get_event_loop().run_until_complete(
        set_webhook(bot_app.bot, f"{webhook_host}{webhook_path}")
    )
    return bot_app


def init_manager_bot():
    """Initialize manager bot with specific handlers"""
    global MANAGER_BOT
    handlers = [
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_codewriting),
        CommandHandler("start", start),
        CommandHandler("create", create),
        CommandHandler("grant", grant),
        CommandHandler("revoke", revoke),
        CommandHandler("list_users", list_users),
    ]
    MANAGER_BOT = _init_bot(config.manager_bot_token, handlers, "/webhook/manager")


def init_example_bot():
    """Initialize example bot with specific handlers"""
    global EXAMPLE_BOT
    handlers = [MessageHandler(filters.TEXT & ~filters.COMMAND, example_echo)]
    EXAMPLE_BOT = _init_bot(config.example_bot_token, handlers, "/webhook/example")


def init_rnp_bot():
    """Initialize RNP bot with specific handlers"""
    global RNP_BOT
    handlers = [
        CommandHandler("start", rnp_start),
        CommandHandler("files", rnp_files),
        CommandHandler("delete", rnp_delete),
        CommandHandler("add", rnp_add),
        CommandHandler("update", rnp_update),
        CommandHandler("select", rnp_select),
        MessageHandler(filters.TEXT & ~filters.COMMAND, rnp_echo),
        MessageHandler(filters.Document.ALL, rnp_document),
    ]
    RNP_BOT = _init_bot(config.rnp_bot_token, handlers, "/webhook/rnp")


def init_bots():
    """Run the FastAPI server for webhooks"""
    # Initialize bots and set webhooks
    init_manager_bot()
    init_example_bot()
    init_rnp_bot()


async def dispatch_manager_update(update_data):
    """Handle and dispatch updates to appropriate handlers."""
    global MANAGER_BOT
    update = Update.de_json(update_data, MANAGER_BOT.bot)
    await MANAGER_BOT.process_update(update)


async def dispatch_example_update(update_data):
    global EXAMPLE_BOT
    update = Update.de_json(update_data, EXAMPLE_BOT.bot)
    await EXAMPLE_BOT.process_update(update)


async def dispatch_rnp_update(update_data):
    global RNP_BOT
    update = Update.de_json(update_data, RNP_BOT.bot)
    log.info("Parsed RNP update: %s", update)
    await RNP_BOT.process_update(update)
