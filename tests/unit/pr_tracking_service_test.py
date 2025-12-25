import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.app.service.pr_tracking_service import PullRequestTrackingService
from src.infrastructure.github.pull_requests_client import PullRequestInfo, PullRequestComment
from src.infrastructure.db.pr_tracking_storage import PullRequestTracking


class TestPullRequestTrackingService(unittest.TestCase):
    def setUp(self):
        self.pr_client = Mock()
        self.pr_tracking_storage = Mock()
        self.repository_client = Mock()
        self.llm_client = Mock()
        self.code_builder = Mock()
        self.log = Mock()

        self.service = PullRequestTrackingService(
            self.pr_client,
            self.pr_tracking_storage,
            self.repository_client,
            self.llm_client,
            self.code_builder,
            self.log,
        )

    def test_track_pull_requests_calls_client(self):
        # Arrange
        self.pr_client.get_open_pull_requests.return_value = []

        # Act
        self.service.track_pull_requests()

        # Assert
        self.pr_client.get_open_pull_requests.assert_called_once()

    def test_skip_draft_prs(self):
        # Arrange
        draft_pr = PullRequestInfo(
            number=1,
            title="Draft PR",
            body="",
            state="open",
            is_draft=True,
            head_branch="feature",
            base_branch="dev",
            mergeable=True,
            mergeable_state="clean",
            has_conflicts=False,
            comments=[],
            reviews=[],
            approved=False,
            head_sha="abc123",
            base_sha="def456",
        )
        self.pr_client.get_open_pull_requests.return_value = [draft_pr]

        # Act
        self.service.track_pull_requests()

        # Assert - should not process draft PR
        self.pr_tracking_storage.update_comment_check.assert_not_called()

    def test_check_new_comments(self):
        # Arrange
        comment = PullRequestComment(
            id=1,
            author="test-user",
            body="Please fix this",
            created_at=datetime.now(),
            is_review_comment=False,
        )
        pr = PullRequestInfo(
            number=1,
            title="Test PR",
            body="",
            state="open",
            is_draft=False,
            head_branch="feature",
            base_branch="dev",
            mergeable=True,
            mergeable_state="clean",
            has_conflicts=False,
            comments=[comment],
            reviews=[],
            approved=False,
            head_sha="abc123",
            base_sha="def456",
        )
        self.pr_client.get_open_pull_requests.return_value = [pr]
        self.pr_tracking_storage.get_tracking.return_value = None
        self.llm_client.send_prompt.return_value = "ACTION: ACKNOWLEDGE\nSUMMARY: Will review"

        # Act
        self.service.track_pull_requests()

        # Assert
        self.pr_tracking_storage.update_comment_check.assert_called_once_with(1)

    def test_merge_approved_pr(self):
        # Arrange
        pr = PullRequestInfo(
            number=1,
            title="Test PR",
            body="",
            state="open",
            is_draft=False,
            head_branch="feature",
            base_branch="dev",
            mergeable=True,
            mergeable_state="clean",
            has_conflicts=False,
            comments=[],
            reviews=["APPROVED"],
            approved=True,
            head_sha="abc123",
            base_sha="def456",
        )
        self.pr_client.get_open_pull_requests.return_value = [pr]
        self.pr_tracking_storage.get_tracking.return_value = PullRequestTracking(
            pr_number=1, base_branch_sha="def456", head_branch_sha="abc123"
        )
        self.pr_client.merge_pull_request.return_value = True

        # Act
        self.service.track_pull_requests()

        # Assert
        self.pr_client.merge_pull_request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
