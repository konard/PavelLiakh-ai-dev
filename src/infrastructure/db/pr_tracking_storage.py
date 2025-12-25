from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from tinydb import Query
from src.infrastructure.db.json_storage import JsonStorage


@dataclass
class PullRequestTracking:
    """Track the state of a pull request for monitoring purposes."""

    pr_number: int
    last_comment_check: Optional[str] = None  # ISO format datetime
    last_conflict_check: Optional[str] = None  # ISO format datetime
    last_approval_check: Optional[str] = None  # ISO format datetime
    base_branch_sha: Optional[str] = None
    head_branch_sha: Optional[str] = None
    _id: Optional[str] = None


class PullRequestTrackingStorage:
    """Storage for tracking pull request monitoring state."""

    def __init__(self, storage: JsonStorage, log):
        self.storage = storage
        self.log = log
        self.pr_tracking_db = self.storage.get_db("pr_tracking")

    def get_tracking(self, pr_number: int) -> Optional[PullRequestTracking]:
        """Get tracking information for a specific PR."""
        return self.storage._find_entity(
            db=self.pr_tracking_db,
            query=Query().pr_number == pr_number,
            entity_class=PullRequestTracking,
        )

    def save_tracking(self, tracking: PullRequestTracking) -> PullRequestTracking:
        """Save or update tracking information for a PR."""
        return self.storage.save_entity(
            db=self.pr_tracking_db,
            query=Query().pr_number == tracking.pr_number,
            entity=tracking,
            entity_class=PullRequestTracking,
        )

    def update_comment_check(self, pr_number: int) -> None:
        """Update the last comment check timestamp."""
        tracking = self.get_tracking(pr_number)
        if not tracking:
            tracking = PullRequestTracking(pr_number=pr_number)
        tracking.last_comment_check = datetime.now().isoformat()
        self.save_tracking(tracking)

    def update_conflict_check(self, pr_number: int, base_sha: str, head_sha: str) -> None:
        """Update the last conflict check timestamp and branch SHAs."""
        tracking = self.get_tracking(pr_number)
        if not tracking:
            tracking = PullRequestTracking(pr_number=pr_number)
        tracking.last_conflict_check = datetime.now().isoformat()
        tracking.base_branch_sha = base_sha
        tracking.head_branch_sha = head_sha
        self.save_tracking(tracking)

    def update_approval_check(self, pr_number: int) -> None:
        """Update the last approval check timestamp."""
        tracking = self.get_tracking(pr_number)
        if not tracking:
            tracking = PullRequestTracking(pr_number=pr_number)
        tracking.last_approval_check = datetime.now().isoformat()
        self.save_tracking(tracking)
