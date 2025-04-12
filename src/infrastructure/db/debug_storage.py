import json
import os
from datetime import datetime

from src.config import config
from src.ioc import log


def store_debug_info(debug_info):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"conversation-{timestamp}.json"
    file_path = os.path.join(config.debug_folder_path, file_name)

    log.info(f"Storing debug info to {os.getcwd()}/{file_path}")
    print(f"Storing debug info to {os.getcwd()}/{file_path}")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(debug_info, f, indent=4, ensure_ascii=False)
