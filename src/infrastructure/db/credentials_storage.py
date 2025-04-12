from typing import Optional
from dataclasses import dataclass
from tinydb import Query
from src.infrastructure.db.json_storage import MongoStorage
from src.infrastructure.logger import get_logger
from secrets import compare_digest

log = get_logger(__name__)

@dataclass
class Credentials:
    login: str
    password: str  # Note: In production this should be hashed

class CredentialsStorage:
    def __init__(self, storage: MongoStorage):
        self.storage = storage
        self.credentials_db = self.storage.get_db("credentials")

    def save_credentials(self, credentials: Credentials) -> bool:
        """Save new credentials if login doesn't exist"""
        existing = self._find_credentials(credentials.login)
        if existing:
            return False
        self.storage.save_entity(self.credentials_db, Query().login == credentials.login, credentials, Credentials)
        return True

    def validate_credentials(self, login: str, password: str) -> bool:
        """Check if credentials match"""
        credentials = self._find_credentials(login)
        log.info("Validating credentials for login: %s", login)
        if not credentials:
            return False
        return compare_digest(credentials.password, password)

    def _find_credentials(self, login: str) -> Optional[Credentials]:
        return self.storage._find_entity(
            self.credentials_db, 
            Query().login == login,
            Credentials
        )
