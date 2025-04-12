from typing import List, Optional

from src.config import config
from src.infrastructure.db.json_storage import MongoStorage
from src.app.service.entities import UserFile, User, UserContext
import os

DEFAULT_FILE = "default"
BIG_FILE = "big"


class UserFileService:
    """Service for managing user files and related operations"""

    def __init__(self, storage: MongoStorage, log):
        self.storage = storage
        self.log = log
        self.log.info("Initialized UserFileService")

    def add_file_to_user(self, user_id: str, file: UserFile) -> User:
        """Add or replace a file in user's file list"""
        self.log.info(f"Adding file '{file.original_filename}' to user {user_id}")

        user = self.storage.find_user_by_telegram_id(user_id)
        if not user:
            self.log.error(f"User {user_id} not found")
            raise ValueError(f"User {user_id} not found")

        # Initialize files if needed
        if user.files is None:
            self.log.debug(f"Initializing files list for user {user_id}")
            user.files = []

        # Remove existing file with same name if it exists
        self.log.debug(f"Checking for existing file '{file.original_filename}'")
        self.remove_file(user_id, file.original_filename)

        # Add the new file
        self.log.info(f"Adding new file '{file.original_filename}' ({file.size} bytes)")
        user.files.append(file)
        saved_user = self.storage.save_user(user)
        self.log.debug(f"File added successfully to user {user_id}")
        return saved_user

    def get_user_files(self, user_id: str) -> List[UserFile]:
        """Get all files for a user"""
        self.log.debug(f"Getting files for user {user_id}")

        user = self.storage.find_user_by_telegram_id(user_id)

        if not user:
            self.log.debug(f"User {user_id} not found")
            return []

        if not user.files:
            self.log.debug(f"No files found for user {user_id}")
            return []

        self.log.debug(f"Found {len(user.files)} files for user {user_id}")
        return user.files

    def get_file_by_name(self, user: User, filename: str) -> Optional[UserFile]:
        """Get a specific file by name for a user"""
        self.log.debug(f"Looking for file '{filename}' for user {user.telegram_id}")

        files = self.get_user_files(user.telegram_id)
        file = next((f for f in files if f.original_filename == filename), None)

        if file:
            self.log.debug(f"Found file '{filename}' for user {user.telegram_id}")
        else:
            self.log.debug(f"File '{filename}' not found for user {user.telegram_id}")

        return file

    def remove_file(self, user_id: str, filename: str) -> User:
        """Remove a file from user's file list and delete it from disk"""
        self.log.info(f"Removing file '{filename}' for user {user_id}")

        user = self.storage.find_user_by_telegram_id(user_id)
        if not user:
            self.log.debug(f"User {user_id} not found")
            return None

        if not user.files:
            self.log.debug(f"No files found for user {user_id}")
            return user

        for f in user.files:
            if f.original_filename == filename:
                self.log.debug(f"Found file '{filename}' at path {f.path}")
                try:
                    if os.path.exists(f.path):
                        self.log.debug(f"Deleting file from disk: {f.path}")
                        os.remove(f.path)
                        self.log.info(f"Successfully deleted file {f.path}")
                    else:
                        self.log.warning(f"File path {f.path} does not exist")
                except OSError as e:
                    self.log.error(f"Error deleting file {f.path}: {e}")
                    raise

        # Remove the file from the user's file list
        user.files = [f for f in user.files if f.original_filename != filename]
        self.log.debug(f"Removed file '{filename}' from user's file list")

        if not user.context:
            self.log.debug(f"Initializing context for user {user_id}")
            user.context = UserContext(current_file=DEFAULT_FILE)

        saved_user = self.storage.save_user(user)
        self.log.info(f"File '{filename}' removed successfully for user {user_id}")
        return saved_user

    def get_current_filename(self, user: User) -> str:
        """Get the current file name from user context"""
        if not user:
            self.log.debug("No user provided, returning default file")
            return DEFAULT_FILE

        if user.context and user.context.current_file:
            self.log.debug(f"Current file for user {user.telegram_id}: {user.context.current_file}")
            return user.context.current_file

        self.log.debug(f"No current file set for user {user.telegram_id}, returning default")
        return DEFAULT_FILE

    def get_current_file_path(self, user: User = None):
        """Get the current file path from user context"""
        name = self.get_current_filename(user)
        self.log.debug(f"Getting path for current file '{name}'")

        if name == DEFAULT_FILE:
            path = config.get_resource("tests/benchmark/files/sales_data.csv")
            self.log.debug(f"Using default file at {path}")
            return path
        elif name == BIG_FILE:
            path = config.get_resource("tests/benchmark/files/sales_data_big.csv")
            self.log.debug(f"Using big file at {path}")
            return path
        elif name:
            file = self.get_file_by_name(user, name)
            if file:
                self.log.debug(f"Found user file at {file.path}")
                return file.path
            self.log.warning(f"File '{name}' not found for user {user.telegram_id}")
