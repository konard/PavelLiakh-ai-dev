from app.github_client import GitHubClient
from app.storage import IssueStorage, IssueData
from app.gpt_client import generate_code, determine_filepath
from app.git_handler import GitHandler


def fetch_and_store_issues(github_client, storage):
    print("Fetching open issues...")
    issues = github_client.get_open_issues()

    for issue in issues:
        issue_data = IssueData(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            body=issue.body or "",
            processed=False,
            plan=None,
        )
        storage.save_issue(issue_data)


def process_unhandled_issues(storage, git_handler):
    unprocessed = storage.get_unprocessed_issues()

    for issue in unprocessed:
        print(f"\nGenerating code for issue #{issue.number}: {issue.title}")

        try:
            generated_code = generate_code(issue.title, issue.body)

            filepath = determine_filepath(
                issue.number, issue.title, issue.body, generated_code
            )

            pr_url = git_handler.create_branch_commit_pr(
                issue_number=issue.number,
                filepath=filepath,
                code=generated_code,
            )

            storage.mark_issue_as_processed(issue.id, generated_code)

            print(f"Issue #{issue.number} processed.")
            print(f"File: {filepath}")
            print(f"PR created: {pr_url}\n")

        except Exception as e:
            print(f"Error processing issue #{issue.number}: {e}")


if __name__ == "__main__":
    try:
        github_client = GitHubClient()
        git_handler = GitHandler()
        storage = IssueStorage()

        fetch_and_store_issues(github_client, storage)
        process_unhandled_issues(storage, git_handler)

    except Exception as e:
        print(f"An error occurred in main: {e}")
