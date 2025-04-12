from src.app.service.entities import User, UserFile, UserContext
import json
from pathlib import Path
from src.infrastructure.logger import get_logger
from src.ioc import storage, sku_storage, client_service
from src.config import config

log = get_logger(__name__)


def mock_user_from_json(file_path: str) -> User:
    """Create a mock user from a JSON file

    Args:
        file_path: Path to JSON file containing user data

    Returns:
        The created User object

    Example JSON format:
    {
        "telegram_id": "12345",
        "telegram_name": "Test User",
        "telegram_link": "testuser",
        "roles": ["rnp"],
        "files": [
            {
                "original_filename": "data.csv",
                "original_url": "http://example.com/data.csv",
                "size": 1024,
                "path": "/path/to/data.csv"
            }
        ],
        "context": {
            "current_file": "data.csv"
        }
    }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert files to UserFile objects
    files = [
        UserFile(
            original_filename=f["original_filename"],
            original_url=f["original_url"],
            size=f["size"],
            path=f["path"],
        )
        for f in data.get("files", [])
    ]

    # Convert context to UserContext
    context_data = data.get("context", {})
    context = UserContext(current_file=context_data.get("current_file")) if context_data else None

    return mock_user(
        telegram_id=data["telegram_id"], roles=data["roles"], files=files, context=context
    )


def reset_storage() -> None:
    """Clear all collections in storage.

    Args:
        storage: MongoStorage instance to clear
    """
    if not config.is_test():
        raise RuntimeError("Cannot clear all collections in non-test environment")
    storage.clear_all_collections()
    sku_storage.clear_all_skus()
    client_service.storage.clear_all_clients()

    log.info("All collections have been cleared")


def mock_user(telegram_id, roles, files=None, context=None):
    """Create a mock user with optional files and context

    Args:
        telegram_id: User's telegram ID
        roles: Single role (str) or list of roles
        files: Optional list of UserFile objects
        context: Optional dictionary for user context

    Returns:
        The created User object
    """
    # Convert roles to list if it's a string
    roles_list = [roles] if isinstance(roles, str) else roles

    admin_user = User(
        telegram_id=telegram_id,
        telegram_name="Test Admin User",
        telegram_link="fake_user_link",
        roles=roles_list,
        files=files,
        context=context,
    )
    return storage.save_user(admin_user)
