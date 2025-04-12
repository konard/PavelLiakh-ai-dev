import sys

from dotenv import load_dotenv
from datetime import datetime

from src.infrastructure.logger import get_logger
from pathlib import Path
import os
import json
import subprocess

log = get_logger(__name__)

# Project root is the parent of src folder
project_root = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
load_dotenv()

PROD_ENV_NAME = "PROD"
DEV_ENV_NAME = "DEV"


def get_ip_from_file():
    """
    Reads the IP address from a file located in either "../instance" or "instance".
    Logs the path to the file once found. Raises an error if the file cannot be read.

    Returns:
        str: The IP address read from the file.

    Raises:
        FileNotFoundError: If no file exists in the specified paths.
        ValueError: If the file is empty or contains invalid data.
    """
    # Paths to check
    paths = ["tg-assist/instance_ip.txt", "../instance_ip.txt", "instance_ip.txt"]

    for path in paths:
        if os.path.exists(path):
            log.info(f"File found: {os.path.abspath(path)}")
            with open(path, encoding="utf-8") as f:
                ip_address = f.read().strip()
                if ip_address:
                    return ip_address

    raise FileNotFoundError(f"No valid instance_ip.txt file found in the {paths}.")


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


"""
This one is an abstraction of Environment config. 
See https://12factor.net/config
"""


class Config:
    def __init__(self):
        # #1 Independent variables
        self.port = 8443
        self.env_name = os.getenv("ENV_NAME", DEV_ENV_NAME).upper()

        is_test = self._is_running_in_test()
        if self.is_test():
            log.warning("Running in test environment, using test configuration")

        self.version = get_git_commit_short_hash()
        print(f"App Version: {self.version}")
        self.root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"Root folder: {self.root_folder}")

        self.debug_folder_path = (
            self.get_folder("tests/debug") if is_test else self.get_folder("debug")
        )
        self.file_storage_path = (
            self.get_folder("tests/file_storage") if is_test else self.get_folder("file_storage")
        )
        os.makedirs(self.debug_folder_path, exist_ok=True)

        # #2 Dependent variables
        self.cert = self.get_resource("cicd/secrets/server.crt")
        self.cert_key = self.get_resource("cicd/secrets/server.key")

        self.manager_bot_token = (
            "test_manager_bot_token" if is_test else get_required_env("MANAGER_BOT_TOKEN")
        )
        self.manager_bot_link = (
            "test_manager_bot_link" if is_test else get_required_env("MANAGER_BOT_LINK")
        )
        self.example_bot_token = (
            "test_example_bot_token" if is_test else get_required_env("EXAMPLE_BOT_TOKEN")
        )
        self.example_bot_link = (
            "test_example_bot_link" if is_test else get_required_env("EXAMPLE_BOT_LINK")
        )
        self.rnp_bot_token = "test_rnp_bot_token" if is_test else get_required_env("RNP_BOT_TOKEN")
        self.rnp_bot_link = "test_rnp_bot_link" if is_test else get_required_env("RNP_BOT_LINK")
        self.storage_path = (
            self.get_folder("tests/test-storage") if is_test else self.get_folder("storage")
        )

        self.admin_telegram_id = "123456789" if is_test else get_required_env("ADMIN_TELEGRAM_ID")
        self.openai_api_key = (
            "test_openai_api_key" if is_test else get_required_env("OPENAI_API_KEY")
        )
        self.deepseek_api_key = (
            "test_deepseek_api_key" if is_test else get_required_env("DEEPSEEK_API_KEY")
        )
        self.ip_address = "127.0.0.1" if (is_test or self.is_dev()) else get_ip_from_file()
        self.google_api_key = (
            "test_google_api_key" if is_test else get_required_env("GOOGLE_API_KEY")
        )

    def is_test(self):
        return self._is_running_in_test()

    def is_dev(self):
        return self.env_name == DEV_ENV_NAME

    def is_prod(self):
        return self.env_name == PROD_ENV_NAME

    def _is_running_in_test(self):
        return "pytest" in sys.modules

    def populate_template(self, input_filename: str):
        # Create temporal json file
        temporal_dir = self.get_folder("temporal")
        output_filename = os.path.join(temporal_dir, "output.json")

        # Read the JSON file
        with open(self.get_resource(input_filename), "r") as file:
            data = json.load(file)

        # Replace placeholder value
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]  # Extract variable name inside ${}
                if env_var == "GOOGLE_API_KEY":
                    data[key] = self.google_api_key

        # Ensure the temporal directory exists
        os.makedirs(temporal_dir, exist_ok=True)

        # Write the modified JSON to the temporal directory
        with open(output_filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        populated_file = self.get_resource(output_filename)
        print(f"Populated JSON file saved to {populated_file}")
        return populated_file

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
