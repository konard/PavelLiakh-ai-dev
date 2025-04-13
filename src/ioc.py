"""This is the Inversion of Control / Dependency Injection container implementation"""
from src.app.story_workflow import StoryWorkflow
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.github.issues_client import IssuesClient

from src.infrastructure.logger import get_logger

# Create instances of services
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = JsonStorage()
llm_client = LlmClient(log=log)

issues_client = IssuesClient()
story_workflow = StoryWorkflow(issues_client)

log.info("Initialized IoC container")
