import logging
from typing import NoReturn
import threading

from src.ui.site.gui import init_ui

from src.app.google_sheet_indicators import start_indicator_process
from src.infrastructure.logger import setup_logging
from src.infrastructure.db.migrations import run_migrations
from src.infrastructure.telegram.telegram_bots import init_bots
from src.config import config
from src.infrastructure.web_server import run_webserver

logger = logging.getLogger(__name__)

from src.ioc import sku_service # dont remove

import src.ui.rest.system_api # dont remove

def main() -> NoReturn:
    setup_logging()
    logger.info("Starting application initialization")

    logger.info("Running database migrations")
    run_migrations()

    logger.debug("Initializing Telegram bots")
    if config.is_prod():
        init_bots()

    # sku_service.process_all_files()
    logger.info(f"SKUs total: {len(sku_service.get_all_skus())}")

    if config.is_prod():
        logger.info("Starting indicator process")
        thread = threading.Thread(target=start_indicator_process, daemon=True)
        thread.start()

    logger.info("Initializing GUI")
    init_ui()

    logger.info(f"Application version is {config.version}")
    logger.info("Starting web server")
    run_webserver()


if __name__ == "__main__":
    main()
