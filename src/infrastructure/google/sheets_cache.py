import json
import os

from src.config import config

# initializes folder
config.get_folder("cache")

cache_filepath = config.get_resource_path("cache/google_sheets_cache.json")


def load_cache_from_file():
    """Loads the cache from a file and returns a dictionary. If the file does not exist, returns an empty dictionary."""
    if os.path.exists(cache_filepath):
        with open(cache_filepath, "r", encoding="utf-8") as f:
            try:
                cache = json.load(f)
                return cache
            except json.JSONDecodeError:
                return {}
    else:
        return {}


def save_cache_to_file(cache):
    """Saves the cache (a dictionary) to a file."""
    with open(cache_filepath, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
