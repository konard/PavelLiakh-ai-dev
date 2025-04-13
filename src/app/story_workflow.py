from dataclasses import dataclass
from typing import Optional

from src.infrastructure.github.issues_client import IssuesClient


class StoryWorkflow:
    def __init__(self, issues_client: IssuesClient):
        self.issues_client = issues_client

    def find_updates(self) -> bool:
        issues = self.issues_client.get_opened_issues()

        process_current_issues = []




        # 1 read stories in github
        # 2 filter those are with label `TODO`
        # 3 store new to DB
        # 4 replace github label with  `IN_PROGRESS`

        print(f"Finding updates for the story: {self.story.title}")
        # Additional logic to find updates in the story workflow

    def start(self):


        print(f"Starting the story: {self.story.title}")
        # Additional logic to start the story workflow

    def progress(self):
        print(f"Progressing the story: {self.story.title}")
        # Additional logic to progress the story workflow

    def complete(self):
        print(f"Completing the story: {self.story.title}")
        # Additional logic to complete the story workflow

    def _convert_github_issue(self, issue: Issue) -> GithubIssue:
        """Convert PyGithub Issue to our GitHubIssue dataclass"""
        return GithubIssue(
            title=issue.title,
            number=issue.number,
            state=issue.state,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
            created_at=issue.created_at.isoformat(),
            updated_at=issue.updated_at.isoformat(),
            url=issue.html_url
        )