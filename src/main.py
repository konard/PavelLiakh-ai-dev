import logging
from typing import NoReturn

from src.ui.site.gui import init_ui

from src.infrastructure.logger import setup_logging
from src.config import config
from src.infrastructure.web_server import run_webserver

from nicegui import ui
from src.poc.ui import create_ui


logger = logging.getLogger(__name__)
from src.ioc import ai_dev_workflow


def main() -> NoReturn:
    setup_logging()
    logger.info("Starting application initialization")

    logger.info(f"Application version is {config.version}")

    ai_dev_workflow.run_ai_dev_workflow()
    # create_ui()
    # ui.run(title="My NiceGUI App", host="localhost", port=8088)


if __name__ in {"__main__", "__mp_main__"}:
    main()
