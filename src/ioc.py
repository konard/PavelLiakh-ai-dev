"""This is the Inversion of Control / Dependency Injection container implementation"""

from src.app.service.planner_service import PlannerService
from src.app.service.story_service import StoryService
from src.app.story_workflow import StoryWorkflow
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.cicd.code_builder import CodeBuilder
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.github.git_repo_client import GitRepoClient
from src.infrastructure.github.issues_client import IssuesClient

from src.infrastructure.logger import get_logger

# infrastructure: low level dependencies
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = JsonStorage()
llm_client = LlmClient(log=log)
issues_client = IssuesClient(log)
git_repo_client = GitRepoClient(log)

# services: logic units
planner_service = PlannerService(llm_client, log)
code_builder = CodeBuilder()
story_storage = StoryStorage(storage, log)
story_service = StoryService(issues_client, story_storage, log)

# high-level workflow structures
story_workflow = StoryWorkflow(issues_client, planner_service, code_builder, story_service, log)

log.info("Initialized IoC container")
