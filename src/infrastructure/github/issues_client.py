from typing import List, Dict
import requests
from dataclasses import dataclass
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

class IssuesClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {config.github_api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.repo = config.github_repo_name

    def get_issues(self, state: str = "open") -> List[GitHubIssue]:
        """Fetch issues from GitHub repository"""
        url = f"{self.base_url}/repos/{self.repo}/issues"
        params = {"state": state}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            issues = []
            for item in response.json():
                issue = GitHubIssue(
                    title=item["title"],
                    number=item["number"],
                    state=item["state"],
                    body=item["body"] or "",
                    labels=[label["name"] for label in item.get("labels", [])]
                )
                issues.append(issue)
            return issues
            
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to fetch GitHub issues: {e}")
            raise
