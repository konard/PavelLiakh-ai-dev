from src.infrastructure.db.credentials_storage import CredentialsStorage, Credentials

class AuthService:
    def __init__(self, credentials_storage: CredentialsStorage):
        self.credentials_storage = credentials_storage

    def register(self, login: str, password: str) -> bool:
        """Register new user credentials"""
        return self.credentials_storage.save_credentials(
            Credentials(login=login, password=password)
        )

    def authenticate(self, login: str, password: str) -> bool:
        """Validate user credentials"""
        return self.credentials_storage.validate_credentials(login, password)
