import unittest
from dataclasses import dataclass
from pathlib import Path
import tempfile
import shutil

from tinydb import Query

from src.infrastructure.db.json_storage import JsonStorage


@dataclass
class TestEntity:
    _id: str = None
    name: str = None
    value: int = None


class TestJsonStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_storage_path = JsonStorage.storage_path
        JsonStorage.storage_path = self.test_dir
        self.storage = JsonStorage()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        JsonStorage.storage_path = self.original_storage_path

    def test_get_db_creates_database(self):
        db = self.storage.get_db("test_collection")

        assert db is not None
        db_file = Path(self.test_dir) / "test_collection.json"
        assert db_file.exists()

    def test_get_db_returns_same_instance_for_same_collection(self):
        db1 = self.storage.get_db("test_collection")
        db2 = self.storage.get_db("test_collection")

        assert db1 is db2

    def test_save_entity_inserts_new_entity(self):
        db = self.storage.get_db("entities")
        entity = TestEntity(_id="1", name="Test", value=42)

        result = self.storage.save_entity(
            db, Query().name == "Test", entity, TestEntity
        )

        assert result.name == "Test"
        assert result.value == 42
        assert len(db.all()) == 1

    def test_save_entity_updates_existing_entity(self):
        db = self.storage.get_db("entities")
        entity1 = TestEntity(_id="1", name="Test", value=42)
        self.storage.save_entity(db, Query().name == "Test", entity1, TestEntity)

        entity2 = TestEntity(_id="1", name="Test", value=99)
        result = self.storage.save_entity(db, Query().name == "Test", entity2, TestEntity)

        assert result.value == 99
        assert len(db.all()) == 1

    def test_save_entity_removes_id_field(self):
        db = self.storage.get_db("entities")
        entity = TestEntity(_id="should_be_removed", name="Test", value=10)

        self.storage.save_entity(db, Query().name == "Test", entity, TestEntity)

        stored_data = db.all()[0]
        assert "_id" not in stored_data

    def test_find_entity_returns_entity_when_exists(self):
        db = self.storage.get_db("entities")
        entity = TestEntity(name="FindMe", value=123)
        self.storage.save_entity(db, Query().name == "FindMe", entity, TestEntity)

        result = self.storage._find_entity(db, Query().name == "FindMe", TestEntity)

        assert result is not None
        assert result.name == "FindMe"
        assert result.value == 123

    def test_find_entity_returns_none_when_not_exists(self):
        db = self.storage.get_db("entities")

        result = self.storage._find_entity(db, Query().name == "NotExists", TestEntity)

        assert result is None


if __name__ == "__main__":
    unittest.main()
