from pathlib import Path
from typing import Any, Optional

from tinydb import TinyDB, Query

from src.app.service.entities import Bot, ConversationMessage, ErrorLog, User, UserFile, UserContext
from src.infrastructure.logger import get_logger
from src.config import config
from dataclasses import asdict

log = get_logger(__name__)


class MongoStorage:
    storage_path = config.storage_path

    def __init__(self):
        log.info(f"Storage path: {Path(self.storage_path).absolute()}")
        self._dbs = {}
        self.users_db = self.get_db("users")
        self.bots_db = self.get_db("bots")
        self.errors_db = self.get_db("errors")
        self.conversations_db = self.get_db("conversations")

    def get_db(self, collection_name: str) -> TinyDB:
        if collection_name not in self._dbs:
            self._dbs[collection_name] = TinyDB(f"{self.storage_path}/{collection_name}.json")
        return self._dbs[collection_name]

    def save_entity(self, db: TinyDB, query: Query, entity: Any, entity_class: type) -> Any:
        entity_data = asdict(entity)
        if "revenue_by_day" in entity_data:
            entity_data["revenue_by_day"] = {
                d.isoformat(): r for d, r in entity_data["revenue_by_day"].items()
            }

        if "sales_by_day" in entity_data:
            entity_data["sales_by_day"] = {
                d.isoformat(): r for d, r in entity_data["sales_by_day"].items()
            }

        if "price_by_day" in entity_data:
            entity_data["price_by_day"] = {
                d.isoformat(): r for d, r in entity_data["price_by_day"].items()
            }

        entity_data.pop("_id", None)

        match = db.contains(query)
        if match:
            db.update(entity_data, query)
        else:
            db.insert(entity_data)
        return entity_class(**entity_data)

    def _find_entity(self, db: TinyDB, query: Query, entity_class: type) -> Optional[Any]:
        entity_data = db.get(query)
        if entity_data:
            # Convert file dicts back to UserFile instances
            if "files" in entity_data and isinstance(entity_data["files"], list):
                entity_data["files"] = [UserFile(**file) for file in entity_data["files"]]
            if "context" in entity_data and entity_data["context"]:
                entity_data["context"] = UserContext(**entity_data["context"])
            return entity_class(**entity_data)
        return None

    def save_user(self, user: User) -> User:
        return self.save_entity(
            db=self.users_db,
            query=Query().telegram_id == user.telegram_id,
            entity=user,
            entity_class=User,
        )

    def find_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        return self._find_entity(
            db=self.users_db, query=Query().telegram_id == telegram_id, entity_class=User
        )

    def find_user_by_telegram_link(self, telegram_link: str) -> Optional[User]:
        return self._find_entity(
            db=self.users_db, query=Query().telegram_link == telegram_link, entity_class=User
        )

    def store_error(self, error_log: ErrorLog) -> None:
        self.errors_db.insert(error_log.__dict__)

    def save_bot(self, bot: Bot) -> Bot:
        return self.save_entity(
            db=self.bots_db, query=Query().token == bot.token, entity=bot, entity_class=Bot
        )

    def find_bot_by_token(self, token: str) -> Optional[Bot]:
        return self._find_entity(db=self.bots_db, query=Query().token == token, entity_class=Bot)

    def find_bot_by_link(self, link: str) -> Optional[Bot]:
        return self._find_entity(db=self.bots_db, query=Query().link == link, entity_class=Bot)

    def get_all_bots(self) -> list[Bot]:
        return [Bot(**bot_data) for bot_data in self.bots_db.all()]

    def save_conversation(self, message: ConversationMessage) -> None:
        self.conversations_db.insert(message.__dict__)

    def get_all_users(self) -> list[User]:
        return [User(**user_data) for user_data in self.users_db.all()]

    def clear_all_collections(self) -> None:
        if not config.is_test():
            log.warning("Cannot clear all collections in non-test environment.")
            return
        else:
            log.info("Clearing all collections...")
        self.users_db.truncate()
        self.bots_db.truncate()
        self.errors_db.truncate()
        self.conversations_db.truncate()
        log.info("All collections have been cleared.")

    def find_errors(self, user_id: str = None) -> list[ErrorLog]:
        query = Query()
        if user_id:
            query = query.user_id == user_id
        else:
            query = None  # No query means return all logs

        results = self.errors_db.search(query) if query else self.errors_db.all()
        return [ErrorLog(**error_data) for error_data in results]
