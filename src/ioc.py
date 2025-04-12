"""This is the Inversion of Control / Dependency Injection container implementation"""
from src.app.service.auth_service import AuthService
from src.infrastructure.db.credentials_storage import CredentialsStorage
from src.app.mp.statistics_service import StatisticsService
from src.app.mp.sku_service import SkuService
from src.infrastructure.db.sku_storage import SkuStorage
from src.infrastructure.google.sheets_parser import GoogleSheetsParser
from src.infrastructure.db.glossary_store import GlossaryStore
from src.infrastructure.pandas_executor import PandasScriptExecutor
from src.app.service.bot_service import BotService
from src.app.service.conversation_service import ConversationService
from src.app.service.error_service import ErrorService
from src.app.service.users_service import UsersService
from src.app.service.user_file_service import UserFileService
from src.infrastructure.ai.llm_client import LLMClient
from src.infrastructure.db.json_storage import MongoStorage
from src.infrastructure.db.client_storage import ClientStorage
from src.app.service.client_service import ClientService
from src.infrastructure.logger import get_logger

# Create instances of services
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = MongoStorage()
llm_client = LLMClient(log=log)
error_service = ErrorService(storage, log)
users_service = UsersService(storage, log, error_service)
user_file_service = UserFileService(storage, log)
bot_service = BotService(storage, log, llm_client, error_service)
conversation_service = ConversationService(storage, log, users_service)
pandas_executor = PandasScriptExecutor()
glossary = GlossaryStore()
google_sheet_parser = GoogleSheetsParser(log)

sku_storage = SkuStorage(storage, log)
sku_service = SkuService(sku_storage, log)
statistics_service = StatisticsService(sku_service, log)
client_storage = ClientStorage(storage, log)
client_service = ClientService(client_storage, log)
credentials_storage = CredentialsStorage(storage)
auth_service = AuthService(credentials_storage)

log.info("Initialized IoC container")
