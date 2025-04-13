from typing import List, Optional
from dataclasses import dataclass
from github import Github
from github.Repository import Repository
from github.Issue import Issue
from src.infrastructure.logger import get_logger
from src.config import config

log = get_logger(__name__)

@dataclass
class GitHubIssue:
    title: str
    number: int
    state: str
    body: str
    labels: List[str]
    created_at: str
    updated_at: str
    url: str

class IssuesClient:
    def __init__(self):
        self._github = Github(config.github_api_key)
        self._repo: Optional[Repository] = None

    @property
    def repo(self) -> Repository:
        """Lazy-load the repository"""
        if self._repo is None:
            self._repo = self._github.get_repo(config.github_repo_name)
        return self._repo

    def get_issues(self, state: str = "open") -> List[GitHubIssue]:
        """Get issues from the repository using PyGithub's built-in methods"""
        try:
            return [
                self._convert_github_issue(issue)
                for issue in self.repo.get_issues(state=state)
            ]
        except Exception as e:
            log.error(f"Failed to get issues: {e}")
            raise

    def get_issue(self, number: int) -> GitHubIssue:
        """Get a single issue by number"""
        try:
            return self._convert_github_issue(self.repo.get_issue(number))
        except Exception as e:
            log.error(f"Failed to get issue #{number}: {e}")
            raise

    def _convert_github_issue(self, issue: Issue) -> GitHubIssue:
        """Convert PyGithub Issue to our GitHubIssue dataclass"""
        return GitHubIssue(
            title=issue.title,
            number=issue.number,
            state=issue.state,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
            created_at=issue.created_at.isoformat(),
            updated_at=issue.updated_at.isoformat(),
            url=issue.html_url
        )
