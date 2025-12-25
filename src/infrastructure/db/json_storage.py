from pathlib import Path
from typing import Any, Optional

from tinydb import TinyDB, Query

from src.infrastructure.logger import get_logger
from src.config import config
from dataclasses import asdict

log = get_logger(__name__)


class JsonStorage:
    storage_path = config.storage_path

    def __init__(self):
        log.info(f"Storage path: {Path(self.storage_path).absolute()}")
        self._dbs = {}

    def get_db(self, collection_name: str) -> TinyDB:
        if collection_name not in self._dbs:
            self._dbs[collection_name] = TinyDB(f"{self.storage_path}/{collection_name}.json")
        return self._dbs[collection_name]

    def save_entity(self, db: TinyDB, query: Query, entity: Any, entity_class: type) -> Any:
        entity_data = asdict(entity)
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
            return entity_class(**entity_data)
        return None

    def clear_all_collections(self) -> None:
        for db_name, db in self._dbs.items():
            db.truncate()
            log.info(f"Cleared collection: {db_name}")
