"""
This one is an abstraction of Environment config.
See https://12factor.net/config
"""

import sys

from dotenv import load_dotenv
from datetime import datetime

from src.infrastructure.logger import get_logger
from pathlib import Path
import os
import subprocess

log = get_logger(__name__)

project_root = Path(__file__).resolve().parent.parent
load_dotenv()

PROD_ENV_NAME = "PROD"
DEV_ENV_NAME = "DEV"


def get_git_commit_short_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        return f"Unknown {datetime.now()}"


def get_required_env(var_name: str) -> str:
    """Get required environment variable or raise EnvironmentError if not set"""
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"{var_name} environment variable is not set")
    return value


class Config:
    def __init__(self):
        # 1 Independent variables
        self.port = 80
        self.env_name = os.getenv("ENV_NAME", DEV_ENV_NAME).upper()

        is_test = self._is_running_in_test()
        if self.is_test():
            log.warning("Running in test environment, using test configuration")

        self.version = get_git_commit_short_hash()
        print(f"App Version: {self.version}")
        self.root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"Root folder: {self.root_folder}")

        self.workspace = (
            self.get_folder("tests/workspace") if is_test else self.get_folder("workspace")
        )
        os.makedirs(self.workspace, exist_ok=True)

        # 2 Dependent variables
        self.storage_path = (
            self.get_folder("tests/test-storage") if is_test else self.get_folder("storage")
        )

        self.openai_api_key = (
            "test_openai_api_key" if is_test else get_required_env("OPENAI_API_KEY")
        )
        self.deepseek_api_key = (
            "test_deepseek_api_key" if is_test else get_required_env("DEEPSEEK_API_KEY")
        )
        self.ip_address = "127.0.0.1"

    def is_test(self):
        return self._is_running_in_test()

    def is_dev(self):
        return self.env_name == DEV_ENV_NAME

    def is_prod(self):
        return self.env_name == PROD_ENV_NAME

    def _is_running_in_test(self):
        return "pytest" in sys.modules

    def get_resource_path(self, resource_name: str) -> Path:
        resource = Path(self.root_folder) / resource_name
        return resource

    def get_resource(self, resource_name: str) -> Path:
        resource = self.get_resource_path(resource_name)
        if not resource.exists():
            raise FileNotFoundError(f"Resource {resource_name} not found")
        return resource

    def get_folder(self, folder_name: str) -> Path:
        folder = Path(self.root_folder) / folder_name
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            print(f"Folder {folder_name} created")
        return folder


config = Config()
