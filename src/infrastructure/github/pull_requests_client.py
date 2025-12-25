from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.IssueComment import IssueComment
from github.PullRequestReview import PullRequestReview

from src.config import config


@dataclass
class PullRequestComment:
    id: int
    author: str
    body: str
    created_at: datetime
    is_review_comment: bool = False


@dataclass
class PullRequestInfo:
    number: int
    title: str
    body: str
    state: str
    is_draft: bool
    head_branch: str
    base_branch: str
    mergeable: Optional[bool]
    mergeable_state: str
    has_conflicts: bool
    comments: List[PullRequestComment]
    reviews: List[str]
    approved: bool
    head_sha: str
    base_sha: str


class PullRequestsClient:
    """Client for interacting with GitHub Pull Requests."""

    def __init__(self, log):
        self.log = log
        self._github: Github = Github(config.github_api_key)

    def get_open_pull_requests(self) -> List[PullRequestInfo]:
        """Get all open pull requests for the configured repository."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        prs = repo.get_pulls(state="open", base="dev")
        return [self._convert_pull_request(pr) for pr in prs]

    def get_pull_request(self, pr_number: int) -> PullRequestInfo:
        """Get a specific pull request by number."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        pr = repo.get_pull(pr_number)
        return self._convert_pull_request(pr)

    def get_new_comments(
        self, pr_number: int, since: Optional[datetime] = None
    ) -> List[PullRequestComment]:
        """Get new comments on a pull request since a specific time."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        pr = repo.get_pull(pr_number)

        comments = []

        # Get issue comments
        issue_comments = pr.get_issue_comments()
        for comment in issue_comments:
            if since is None or comment.created_at > since:
                comments.append(
                    PullRequestComment(
                        id=comment.id,
                        author=comment.user.login,
                        body=comment.body,
                        created_at=comment.created_at,
                        is_review_comment=False,
                    )
                )

        # Get review comments
        review_comments = pr.get_review_comments()
        for comment in review_comments:
            if since is None or comment.created_at > since:
                comments.append(
                    PullRequestComment(
                        id=comment.id,
                        author=comment.user.login,
                        body=comment.body,
                        created_at=comment.created_at,
                        is_review_comment=True,
                    )
                )

        # Sort by created_at
        comments.sort(key=lambda c: c.created_at)
        return comments

    def add_comment(self, pr_number: int, comment: str) -> None:
        """Add a comment to a pull request."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment)
        self.log.info(f"Added comment to PR #{pr_number}")

    def merge_pull_request(
        self, pr_number: int, commit_title: str = None, commit_message: str = None
    ) -> bool:
        """Merge a pull request."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        pr = repo.get_pull(pr_number)

        try:
            result = pr.merge(
                commit_title=commit_title, commit_message=commit_message, merge_method="merge"
            )
            if result.merged:
                self.log.info(f"Successfully merged PR #{pr_number}")
                return True
            else:
                self.log.error(f"Failed to merge PR #{pr_number}: {result.message}")
                return False
        except Exception as e:
            self.log.error(f"Error merging PR #{pr_number}: {str(e)}")
            return False

    def is_approved(self, pr_number: int) -> bool:
        """Check if a pull request has been approved."""
        repo: Repository = self._github.get_repo(config.github_repo_name)
        pr = repo.get_pull(pr_number)

        reviews = pr.get_reviews()
        approved_reviews = [r for r in reviews if r.state == "APPROVED"]

        return len(approved_reviews) > 0

    def _convert_pull_request(self, pr: PullRequest) -> PullRequestInfo:
        """Convert GitHub PullRequest to our PullRequestInfo dataclass."""
        # Get all comments
        comments = self.get_new_comments(pr.number)

        # Get reviews
        reviews = pr.get_reviews()
        review_states = [review.state for review in reviews]

        # Check if approved
        approved = any(state == "APPROVED" for state in review_states)

        # Check for conflicts
        has_conflicts = pr.mergeable is False or pr.mergeable_state in [
            "dirty",
            "conflicting",
        ]

        return PullRequestInfo(
            number=pr.number,
            title=pr.title,
            body=pr.body or "",
            state=pr.state,
            is_draft=pr.draft,
            head_branch=pr.head.ref,
            base_branch=pr.base.ref,
            mergeable=pr.mergeable,
            mergeable_state=pr.mergeable_state,
            has_conflicts=has_conflicts,
            comments=comments,
            reviews=review_states,
            approved=approved,
            head_sha=pr.head.sha,
            base_sha=pr.base.sha,
        )
