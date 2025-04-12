from datetime import datetime

from src.infrastructure.db.json_storage import MongoStorage
from src.app.service.entities import ErrorLog


class ErrorService:
    def __init__(self, storage: MongoStorage, log):
        self.storage = storage
        self.log = log

    def log_error(self, user_id: str, message: str, error: Exception) -> None:
        """Log and store an error"""
        error_log = ErrorLog(
            user_id=user_id,
            message=message,
            timestamp=datetime.now().isoformat(),
            error=str(error),
        )
        self.log.error("Error for user %s: %s", user_id, error, exc_info=True)
        self.storage.store_error(error_log)
