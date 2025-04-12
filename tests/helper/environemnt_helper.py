from fastapi.testclient import TestClient

from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
)
from src.infrastructure.db.migrations import run_migrations
from src.infrastructure.logger import setup_logging
from src.infrastructure.telegram.telegram_api import reset_mock
from src.infrastructure.telegram.telegram_bots import init_bots
from src.infrastructure.web_server import web_app
from tests.helper.db_helper import reset_storage

webhook_client = TestClient(web_app)

import src.ui.rest.bots_api # do not remove
import src.ui.rest.system_api  # do not remove


def prepare_new_test_env():
    set_predefined_llm_response(None)
    reset_mock()
    reset_storage()
    run_migrations()
    setup_logging()
    init_bots()
