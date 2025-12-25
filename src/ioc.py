"""This is the Inversion of Control / Dependency Injection container implementation"""

from src.app.service.code_repo_service import CodeRepoServise
from src.app.service.development_service import DevelopmentService
from src.app.service.planner_service import PlannerService
from src.app.service.code_request_service import CodeRequestService
from src.app.service.story_service import StoryService
from src.app.service.pr_tracking_service import PullRequestTrackingService
from src.app.ai_dev_workflow import AiDevWorkflow
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ci.code_builder import CodeBuilder
from src.infrastructure.db.json_storage import JsonStorage
from src.infrastructure.db.story_storage import StoryStorage
from src.infrastructure.db.pr_tracking_storage import PullRequestTrackingStorage
from src.infrastructure.github.repository_client import RepositoryClient
from src.infrastructure.github.issues_client import IssuesClient
from src.infrastructure.github.pull_requests_client import PullRequestsClient

from src.infrastructure.logger import get_logger

# infrastructure: low level dependencies
log = get_logger(__name__)
log.info("Initializing IoC container")
storage = JsonStorage()
llm_client = LlmClient(log=log)
issues_client = IssuesClient(log)
pr_client = PullRequestsClient(log)
git_repo_client = RepositoryClient(log)
code_builder = CodeBuilder(log, git_repo_client)
story_storage = StoryStorage(storage, log)
pr_tracking_storage = PullRequestTrackingStorage(storage, log)

# services: logic units
planner_service = PlannerService(llm_client, story_storage, log)
code_request_service = CodeRequestService(llm_client, story_storage, log)
story_service = StoryService(issues_client, story_storage, log)
development_service = DevelopmentService(
    llm_client,
    git_repo_client,
    code_builder,
    planner_service,
    code_request_service,
    story_storage,
    log,
)
pr_tracking_service = PullRequestTrackingService(
    pr_client, pr_tracking_storage, git_repo_client, llm_client, code_builder, log
)
code_repo_service = CodeRepoServise(log)

# high-level workflow structures
ai_dev_workflow = AiDevWorkflow(
    issues_client, story_service, development_service, pr_tracking_service, log
)

log.info("Initialized IoC container")
