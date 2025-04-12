from typing import Optional

from src.infrastructure.db.json_storage import MongoStorage
from src.app.domain.client import Client
from tinydb import Query


class ClientStorage:
    def __init__(self, storage: MongoStorage, log):
        self.storage = storage
        self.client_db = self.storage.get_db("clients")
        self.log = log

    def save(self, client: Client) -> Client:
        saved_client = self.storage.save_entity(
            db=self.client_db, 
            query=Query().email == client.email, 
            entity=client, 
            entity_class=Client
        )
        return saved_client

    def find_by_email(self, email: str) -> Optional[Client]:
        query = Query()
        return self.storage._find_entity(
            db=self.client_db, 
            query=query.email == email, 
            entity_class=Client
        )

    def get_all_clients(self) -> list[Client]:
        return [
            self.storage._find_entity(
                db=self.client_db,
                query=Query().email == client_data.get("email"),
                entity_class=Client
            )
            for client_data in self.client_db.all()
        ]

    def clear_all_clients(self) -> None:
        """Remove all clients from storage"""
        self.client_db.truncate()
