import logging
from typing import NoReturn

from src.ui.site.gui import init_ui

from src.infrastructure.logger import setup_logging
from src.config import config
from src.infrastructure.web_server import run_webserver

logger = logging.getLogger(__name__)
from src.ioc import story_workflow


def main() -> NoReturn:
    setup_logging()
    logger.info("Starting application initialization")

    logger.info(f"Application version is {config.version}")

    story_workflow.find_updates()
    story_workflow.plan()


if __name__ == "__main__":
    main()
