from typing import List, Optional
from dataclasses import dataclass
from github.Issue import Issue
from github.Repository import Repository

from src.config import config
from github import Github


@dataclass
class GithubIssue:
    number: Optional[int] = None
    title: Optional[str] = None
    body: Optional[str] = None
    labels: Optional[list[str]] = None
    comments: Optional[list[str]] = None


TODO_LABEL = "TODO"
IN_PROGRESS_LABEL = "IN_PROGRESS"


class IssuesClient:
    def __init__(self, log):
        self.log = log
        self._github: Github = Github(config.github_api_key)

    def get_opened_issues(self) -> list[GithubIssue]:
        self._repo: Repository = self._github.get_repo(config.github_repo_name)
        issues_page = self._repo.get_issues()
        issues = [self._convert_github_issue(issue) for issue in issues_page]

        return issues

    def update_issue_labels(self, issue_number: int, new_labels: list[str]):
        repo = self._github.get_repo(config.github_repo_name)
        issue = repo.get_issue(issue_number)

        issue.edit(labels=new_labels)
        self.log.info(f"Updated labels for issue #{issue_number} to {new_labels}")

    def _convert_github_issue(self, issue: Issue) -> GithubIssue:
        return GithubIssue(
            title=issue.title,
            number=issue.number,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
        )
