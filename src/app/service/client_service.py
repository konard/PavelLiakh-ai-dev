from typing import Optional
from src.app.domain.client import Client
from src.infrastructure.db.client_storage import ClientStorage


class ClientService:
    def __init__(self, storage: ClientStorage, log):
        self.storage = storage
        self.log = log

    def register_client(self, name: str, email: str, sku_number: str) -> Client:
        """Register a new client with their contact info and SKU of interest"""
        client = Client(
            name=name,
            email=email,
            sku_number=sku_number
        )
        saved_client = self.storage.save(client)
        self.log.info(f"Registered new client: {email}")
        return saved_client

    def get_client_by_email(self, email: str) -> Optional[Client]:
        """Retrieve client by their email"""
        return self.storage.find_by_email(email)

    def get_all_clients(self) -> list[Client]:
        """Get all registered clients"""
        return self.storage.get_all_clients()
