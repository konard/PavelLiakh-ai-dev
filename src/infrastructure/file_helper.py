from pathlib import Path
from typing import Optional
import requests
from urllib.parse import urlparse
import uuid

from src.app.service.entities import UserFile
from src.config import config
from src.infrastructure.logger import get_logger

log = get_logger(__name__)


def download_file_from_url(url: str) -> Optional[UserFile]:
    """Download a file from URL and return UserFile metadata"""
    try:
        log.info(f"Starting file download from URL: {url}")

        # Get filename from URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name

        if config.is_test():
            log.info(f"Skipping file download from URL: {url} (test mode)")
            # return fake file
            return UserFile(
                original_url=url, original_filename=filename, size=3000, path="fake/path"
            )

        # Download file content
        response = requests.get(url)
        response.raise_for_status()

        # Save file with unique name
        random_uuid = uuid.uuid4()
        save_path = config.storage_path / f"{random_uuid}_{filename}"
        log.info(f"Saving file to: {save_path}")

        with open(save_path, "wb") as f:
            f.write(response.content)

        log.info(f"File saved successfully, size: {len(response.content)} bytes")

        return UserFile(
            original_filename=filename,
            original_url=url,
            size=len(response.content),
            path=str(save_path),
        )

    except Exception as e:
        log.error(f"Error downloading file from URL {url}: {e}")
        return None


def get_content(resource_name: str):
    file = config.get_resource(resource_name)
    return file.read_text()
