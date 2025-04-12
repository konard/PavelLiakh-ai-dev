"""This is the Inversion of Control / Dependency Injection container implementation"""
from src.infrastructure.ai.llm_client import LLMClient
from src.infrastructure.db.json_storage import MongoStorage

from src.infrastructure.logger import get_logger

# Create instances of services
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = MongoStorage()
llm_client = LLMClient(log=log)

log.info("Initialized IoC container")
