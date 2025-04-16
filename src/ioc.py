"""This is the Inversion of Control / Dependency Injection container implementation"""

from src.app.service.development_service import DevelopmentService
from src.app.service.planner_service import PlannerService
from src.app.service.story_service import StoryService
from src.app.ai_dev_workflow import AiDevWorkflow
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ci.code_builder import CodeBuilder
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.github.repository_client import RepositoryClient
from src.infrastructure.github.issues_client import IssuesClient

from src.infrastructure.logger import get_logger

# infrastructure: low level dependencies
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = JsonStorage()
llm_client = LlmClient(log=log)
issues_client = IssuesClient(log)
git_repo_client = RepositoryClient(log)
code_builder = CodeBuilder(log)
story_storage = StoryStorage(storage, log)

# services: logic units
planner_service = PlannerService(llm_client, story_storage, log)
story_service = StoryService(issues_client, story_storage, log)
development_service = DevelopmentService(
    llm_client, git_repo_client, code_builder, planner_service, story_storage, log
)

# high-level workflow structures
ai_dev_workflow = AiDevWorkflow(issues_client, story_service, development_service, log)

log.info("Initialized IoC container")
