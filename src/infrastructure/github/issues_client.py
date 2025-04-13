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


class IssuesClient:
    def __init__(self, log):
        self.log = log
        self._github: Github = Github(config.github_api_key)
        self._repo: Repository = self._github.get_repo(config.github_repo_name)

    def get_opened_issues(self) -> list[GithubIssue]:
        # FIXME assuming there is one page of issues
        issues_page = self._repo.get_issues()
        issues = issues_page.get_page(0)
        issues = [self._convert_github_issue(issue) for issue in issues]

        return issues

    def update_issue(self, issue: GithubIssue):
        # TODO it must find the issue by number in github. It must set new label in github
        pass

    def _convert_github_issue(self, issue: Issue) -> GithubIssue:
        return GithubIssue(
            title=issue.title,
            number=issue.number,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
        )