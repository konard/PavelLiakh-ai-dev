from fastapi.testclient import TestClient

from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
)
from src.infrastructure.logger import setup_logging
from src.infrastructure.web_server import web_app
from tests.helper.db_helper import reset_storage

webhook_client = TestClient(web_app)


def prepare_new_test_env():
    set_predefined_llm_response(None)
    reset_mock()
    reset_storage()
    setup_logging()
