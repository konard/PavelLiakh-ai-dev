"""
Experiment script to test PR tracking functionality.
This script demonstrates how the PR tracking system works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.logger import get_logger
from src.infrastructure.github.pull_requests_client import PullRequestsClient

log = get_logger(__name__)


def test_get_open_prs():
    """Test fetching open pull requests."""
    log.info("Testing PR tracking functionality")

    pr_client = PullRequestsClient(log)

    try:
        prs = pr_client.get_open_pull_requests()
        log.info(f"Found {len(prs)} open pull requests")

        for pr in prs:
            log.info(f"PR #{pr.number}: {pr.title}")
            log.info(f"  Branch: {pr.head_branch} -> {pr.base_branch}")
            log.info(f"  Draft: {pr.is_draft}")
            log.info(f"  Approved: {pr.approved}")
            log.info(f"  Has conflicts: {pr.has_conflicts}")
            log.info(f"  Comments: {len(pr.comments)}")

    except Exception as e:
        log.error(f"Error testing PR tracking: {str(e)}")
        import traceback

        traceback.print_exc()


def test_check_pr_approval():
    """Test checking if a PR is approved."""
    pr_client = PullRequestsClient(log)

    try:
        # Check PR #30 (our test PR)
        pr_number = 30
        is_approved = pr_client.is_approved(pr_number)
        log.info(f"PR #{pr_number} approved: {is_approved}")

        pr_info = pr_client.get_pull_request(pr_number)
        log.info(f"PR #{pr_number} info:")
        log.info(f"  Title: {pr_info.title}")
        log.info(f"  State: {pr_info.state}")
        log.info(f"  Mergeable: {pr_info.mergeable}")
        log.info(f"  Reviews: {pr_info.reviews}")

    except Exception as e:
        log.error(f"Error checking PR approval: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    log.info("=== Testing PR Tracking ===")
    test_get_open_prs()
    print()
    test_check_pr_approval()
    log.info("=== Test Complete ===")
