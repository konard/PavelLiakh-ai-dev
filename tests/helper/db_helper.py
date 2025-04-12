from src.infrastructure.logger import get_logger
from src.ioc import storage
from src.config import config

log = get_logger(__name__)


def reset_storage() -> None:
    if not config.is_test():
        raise RuntimeError("Cannot clear all collections in non-test environment")
    storage.clear_all_collections()

    log.info("All collections have been cleared")
