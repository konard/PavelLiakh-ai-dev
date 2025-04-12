from pathlib import Path
from typing import Optional

import requests

from src.app.service.entities import UserFile
from src.config import config
from src.infrastructure.logger import get_logger

log = get_logger(__name__)


def download_file(file_id: str, bot_token: str) -> Optional[UserFile]:
    """Download a file from Telegram and return UserFile metadata"""
    log.info(f"Starting file download for file_id: {file_id}")

    if config.is_test():
        log.info("Running in test mode, returning mock file")
        return UserFile(
            original_filename="test_file.csv",
            original_url=f"https://telegram.org/file/{file_id}",
            size=12345,
            path=str(f"test_file_{file_id}.csv"),
        )

    try:
        # Step 1: Get file info
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        log.info(f"Requesting file info from: {file_info_url}")
        response = requests.get(file_info_url)
        file_info = response.json()
        log.info(f"Received file info: {file_info}")

        if not file_info.get("ok"):
            log.error(f"Failed to get file info: {file_info}")
            log.error(f"Response status: {response.status_code}, content: {response.text}")
            return None

        file_path = file_info["result"]["file_path"]
        file_size = file_info["result"]["file_size"]
        original_filename = Path(file_path).name
        log.info(
            f"File info received - path: {file_path}, size: {file_size}, name: {original_filename}"
        )

        # Step 2: Download file content
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        log.info(f"Downloading file from: {download_url}")
        response = requests.get(download_url)

        if response.status_code != 200:
            log.error(f"Failed to download file: {response.status_code} {response.text}")
            log.error(f"Download URL: {download_url}")
            return None

        # Save file with unique name
        save_path = config.storage_path / f"{original_filename}_{file_id}.csv"
        log.info(f"Saving file to: {save_path}")
        with open(save_path, "wb") as f:
            f.write(response.content)
        log.info(f"File saved successfully, size: {len(response.content)} bytes")

        return UserFile(
            original_filename=original_filename,
            original_url=download_url,
            size=file_size,
            path=str(save_path),
        )

    except Exception as e:
        log.error(f"Error downloading file: {e}")
        return None
