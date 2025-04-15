from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
BASE_BRANCH = os.getenv("BASE_BRANCH")


class GitHubClient:
    def __init__(self):
        self.client = Github(GITHUB_TOKEN)
        self.repo = self.client.get_repo(REPO_NAME)

    def get_open_issues(self):
        try:
            return self.repo.get_issues(state="open")
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []

    def get_repo_file_paths(self, branch=BASE_BRANCH):
        tree = self.repo.get_git_tree(
            sha=self.repo.get_branch(branch).commit.sha, recursive=True
        ).tree
        return [item.path for item in tree if item.type == "blob"]


if __name__ == "__main__":
    gh = GitHubClient()
    print("Repo files:", gh.get_repo_file_paths())
