from dataclasses import dataclass
from typing import Optional

from src.infrastructure.github.repository_client import RepoContext


@dataclass
class BuildResult:
    success: bool
    error: Optional[str] = None


class CodeBuilder:
    def __init__(self, log):
        self.log = log

    def check_commit(self, repository_context: RepoContext) -> BuildResult:
        self.log.info(
            f"building code: repo={repository_context.name}, branch={repository_context.branch}"
        )
        # FYI
        # repo url = repository_context.auth_repo_url()
        # branch name = repository_context.branch
        # local path = repository_context.local_path
        return BuildResult(True, None)
