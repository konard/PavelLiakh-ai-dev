import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
BASE_BRANCH = os.getenv("BASE_BRANCH", "main")


class GitHandler:
    def __init__(self):
        self.client = Github(GITHUB_TOKEN)
        self.repo = self.client.get_repo(REPO_NAME)

    def create_branch(self, new_branch_name):
        base_ref = self.repo.get_git_ref(f"heads/{BASE_BRANCH}")
        self.repo.create_git_ref(
            ref=f"refs/heads/{new_branch_name}", sha=base_ref.object.sha
        )
        print(f"Branch created: {new_branch_name}")

    def commit_file(self, branch_name, filepath, code, commit_message):
        try:
            existing_file = self.repo.get_contents(filepath, ref=branch_name)
            self.repo.update_file(
                path=filepath,
                message=commit_message,
                content=code,
                sha=existing_file.sha,
                branch=branch_name,
            )
            print(f"Updated existing file: {filepath}")
        except Exception:
            self.repo.create_file(
                path=filepath,
                message=commit_message,
                content=code,
                branch=branch_name,
            )
            print(f"Created new file: {filepath}")

    def create_pull_request(self, branch_name, title, body=None):
        pr = self.repo.create_pull(
            title=title, body=body or "", head=branch_name, base=BASE_BRANCH
        )
        print(f"Pull Request created: {pr.html_url}")
        return pr.html_url

    def create_branch_commit_pr(self, issue_number, filepath, code):
        branch_name = f"codegen/issue-{issue_number}"
        commit_message = f"Add generated code for issue #{issue_number}"
        pr_title = f"[AI] Generated code for issue #{issue_number}"

        self.create_branch(branch_name)
        self.commit_file(branch_name, filepath, code, commit_message)
        return self.create_pull_request(branch_name, pr_title)
