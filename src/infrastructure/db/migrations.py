from src.infrastructure.db.credentials_storage import Credentials
from src.config import config
from src.infrastructure.logger import get_logger
from src.app.service.entities import ROLE_ADMIN, ROLE_ASSISTANT, ROLE_CODEWRITER, Bot, User
from src.ioc import storage, credentials_storage

log = get_logger(__name__)


def run_migrations():
    log.info("Starting migrations")
    _add_admin_user(storage)
    _add_additional_user(storage)
    _add_bots(storage)
    log.info("Migrations completed successfully")
    credentials_storage.save_credentials(
        Credentials(login="GB7IZUc8NZv7", password="U6AgMysZ7tN2ja7QVkT506PoKC59s5fu"))
    credentials_storage.save_credentials(
        Credentials(login="alex_GB7IZUc8NZv7", password="5vgnhWri2UO3V7F5KqUoL7"))

def _migrate_user(storage, telegram_id: str, roles: list[str]):
    log.info(f"Migrating user with ID: {telegram_id}")

    user = storage.find_user_by_telegram_id(telegram_id)
    if not user:
        log.info("Creating new user")
        user = User(
            _id="",
            telegram_id=telegram_id,
            roles=roles,
        )
        storage.save_user(user)
        log.info("User created successfully")
        return

    roles_updated = False
    for role in roles:
        if role not in user.roles:
            log.info(f"Adding {role} to user")
            user.roles.append(role)
            roles_updated = True

    if roles_updated:
        log.info("Updating user roles")
        storage.save_user(user)
        log.info("User roles updated successfully")


def _add_admin_user(storage):
    _migrate_user(storage, config.admin_telegram_id, [ROLE_ADMIN, ROLE_ASSISTANT, ROLE_CODEWRITER])


def _add_additional_user(storage):
    _migrate_user(
        storage, "540563104", [ROLE_ADMIN, ROLE_ASSISTANT, ROLE_CODEWRITER]  # t.me/homo_habitus1
    )


def _add_bots(storage):
    log.info("Migrating bots")

    existing_bots = storage.get_all_bots()

    manager_bot_exists = any(bot.is_manager for bot in existing_bots)
    if not manager_bot_exists:
        log.info("Creating manager bot")
        manager_bot = Bot(
            _id="",
            owner_id=str(config.admin_telegram_id),
            token=config.manager_bot_token,
            link=f"{config.manager_bot_link}",
            is_manager=True,
            behaviour="I'm assistant manager bot",
        )
        storage.save_bot(manager_bot)
        log.info("Manager bot created successfully")
    else:
        log.info("Manager bot already exists - skipping creation")

    example_bot_exists = any(bot.is_example for bot in existing_bots)
    if not example_bot_exists:
        log.info("Creating example bot")
        example_bot = Bot(
            _id="",
            owner_id=str(config.admin_telegram_id),
            token=config.example_bot_token,
            link=f"{config.example_bot_link}",
            is_example=True,
            behaviour="I'm assistant example bot",
        )
        storage.save_bot(example_bot)
        log.info("Example bot created successfully")
    else:
        log.info("Example bot already exists - skipping creation")

    rnp_bot_exists = any((not bot.is_example and not bot.is_manager) for bot in existing_bots)
    if not rnp_bot_exists:
        log.info("Creating RNP bot")
        rnp_bot = Bot(
            _id="",
            owner_id=str(config.admin_telegram_id),
            token=config.rnp_bot_token,
            link=f"@{config.rnp_bot_link}",
            behaviour="RNP_bot_behavior",
        )
        storage.save_bot(rnp_bot)
        log.info("RNP bot created successfully")
    else:
        log.info("RNP bot already exists - skipping creation")
