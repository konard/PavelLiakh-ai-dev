"""Service for tracking and managing pull requests."""

from datetime import datetime
from typing import Optional

from src.infrastructure.github.pull_requests_client import PullRequestsClient, PullRequestInfo
from src.infrastructure.github.repository_client import RepositoryClient, RepoContext
from src.infrastructure.db.pr_tracking_storage import PullRequestTrackingStorage
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ci.code_builder import CodeBuilder
from src.config import config


class PullRequestTrackingService:
    """Service for periodically tracking pull request status and handling updates."""

    def __init__(
        self,
        pr_client: PullRequestsClient,
        pr_tracking_storage: PullRequestTrackingStorage,
        repository_client: RepositoryClient,
        llm_client: LlmClient,
        code_builder: CodeBuilder,
        log,
    ):
        self.pr_client = pr_client
        self.pr_tracking_storage = pr_tracking_storage
        self.repository_client = repository_client
        self.llm_client = llm_client
        self.code_builder = code_builder
        self.log = log

    def track_pull_requests(self) -> None:
        """Main entry point for tracking all open pull requests."""
        prs = self.pr_client.get_open_pull_requests()
        self.log.info(f"Tracking {len(prs)} open pull requests")

        for pr in prs:
            try:
                self._track_single_pr(pr)
            except Exception as e:
                self.log.error(f"Error tracking PR #{pr.number}: {str(e)}")

    def _track_single_pr(self, pr: PullRequestInfo) -> None:
        """Track a single pull request for updates."""
        self.log.info(f"Checking PR #{pr.number}: {pr.title}")

        # Skip draft PRs
        if pr.is_draft:
            self.log.info(f"PR #{pr.number} is draft, skipping")
            return

        # Check for new comments and resolve them
        self._check_and_resolve_comments(pr)

        # Check for conflicts and resolve them
        self._check_and_resolve_conflicts(pr)

        # Check for approval and merge if ready
        self._check_and_merge_if_approved(pr)

    def _check_and_resolve_comments(self, pr: PullRequestInfo) -> None:
        """Check for new comments and resolve them using LLM."""
        tracking = self.pr_tracking_storage.get_tracking(pr.number)

        # Get new comments since last check
        last_check = None
        if tracking and tracking.last_comment_check:
            last_check = datetime.fromisoformat(tracking.last_comment_check)

        new_comments = [c for c in pr.comments if not last_check or c.created_at > last_check]

        if new_comments:
            self.log.info(f"Found {len(new_comments)} new comments on PR #{pr.number}")
            self._resolve_comments_with_llm(pr, new_comments)

        # Update tracking
        self.pr_tracking_storage.update_comment_check(pr.number)

    def _resolve_comments_with_llm(self, pr: PullRequestInfo, comments) -> None:
        """Use LLM to analyze and respond to PR comments."""
        # Prepare context for LLM
        comments_text = "\n\n".join(
            [
                f"Comment by {c.author} at {c.created_at}:\n{c.body}"
                for c in comments
                if c.author != "github-actions[bot]"  # Skip bot comments
            ]
        )

        if not comments_text:
            return

        prompt = f"""You are reviewing comments on a pull request.

PR Title: {pr.title}
PR Description: {pr.body}

New Comments:
{comments_text}

Analyze these comments and determine if they require code changes or just a response.
If code changes are needed, provide a brief summary of what needs to be changed.
If just a response is needed, draft a professional response.

Format your response as:
ACTION: [CODE_CHANGE or RESPOND or ACKNOWLEDGE]
SUMMARY: [Brief summary of what to do]
RESPONSE: [If ACTION is RESPOND, provide the response text]
"""

        try:
            response = self.llm_client.send_prompt(prompt)
            self.log.info(f"LLM analysis for PR #{pr.number}: {response}")

            # Parse response and take action
            if "RESPOND" in response or "ACKNOWLEDGE" in response:
                # Extract response text if available
                if "RESPONSE:" in response:
                    response_text = response.split("RESPONSE:")[-1].strip()
                    self.pr_client.add_comment(pr.number, response_text)
                else:
                    # Post acknowledgment
                    self.pr_client.add_comment(
                        pr.number,
                        "Thank you for the feedback. The comments have been noted and will be addressed.",
                    )

        except Exception as e:
            self.log.error(f"Error resolving comments with LLM for PR #{pr.number}: {str(e)}")

    def _check_and_resolve_conflicts(self, pr: PullRequestInfo) -> None:
        """Check for merge conflicts and attempt to resolve them."""
        if not pr.has_conflicts:
            return

        self.log.info(f"PR #{pr.number} has conflicts, attempting to resolve")

        tracking = self.pr_tracking_storage.get_tracking(pr.number)

        # Check if base branch has changed
        base_changed = (
            not tracking or not tracking.base_branch_sha or tracking.base_branch_sha != pr.base_sha
        )

        if base_changed:
            self.log.info(f"Base branch has changed for PR #{pr.number}, merging latest changes")
            self._merge_base_branch(pr)
            self.pr_tracking_storage.update_conflict_check(pr.number, pr.base_sha, pr.head_sha)

    def _merge_base_branch(self, pr: PullRequestInfo) -> None:
        """Merge the base branch into the PR branch to resolve conflicts."""
        try:
            repo_context = RepoContext(name=config.github_repo_name, branch=pr.head_branch)
            self.repository_client.checkout_branch(repo_context)

            # Merge base branch
            from git import Repo as GitRepo

            git_repo = GitRepo(self.repository_client._get_local_path(repo_context.name))
            git_repo.remote().fetch()

            try:
                git_repo.git.merge(
                    f"origin/{pr.base_branch}", m=f"Merge {pr.base_branch} into {pr.head_branch}"
                )
                self.log.info(f"Successfully merged {pr.base_branch} into {pr.head_branch}")

                # Push changes
                self.repository_client.push_changes(repo_context)
                self.pr_client.add_comment(
                    pr.number,
                    f"Automatically merged latest changes from `{pr.base_branch}` branch to resolve conflicts.",
                )
            except Exception as merge_error:
                self.log.error(f"Merge conflict detected: {str(merge_error)}")
                self.pr_client.add_comment(
                    pr.number,
                    f"Unable to automatically resolve conflicts. Manual intervention required.\n\nError: {str(merge_error)}",
                )
        except Exception as e:
            self.log.error(f"Error merging base branch for PR #{pr.number}: {str(e)}")

    def _check_and_merge_if_approved(self, pr: PullRequestInfo) -> None:
        """Check if PR is approved and merge if ready."""
        if not pr.approved:
            return

        self.log.info(f"PR #{pr.number} is approved, checking if ready to merge")

        # Check if there are conflicts
        if pr.has_conflicts:
            self.log.info(f"PR #{pr.number} has conflicts, cannot merge yet")
            return

        # Check if base branch has new commits since PR was created
        # If so, rebuild to ensure everything still works
        tracking = self.pr_tracking_storage.get_tracking(pr.number)
        base_changed = (
            not tracking or not tracking.base_branch_sha or tracking.base_branch_sha != pr.base_sha
        )

        if base_changed:
            self.log.info(f"Base branch has new commits for PR #{pr.number}, running build check")
            if not self._verify_build(pr):
                self.pr_client.add_comment(
                    pr.number,
                    "Build check failed after merging latest changes. Please fix the build before merging.",
                )
                return

        # All checks passed, merge the PR
        self.log.info(f"Merging approved PR #{pr.number}")
        success = self.pr_client.merge_pull_request(
            pr.number, commit_title=f"Merge PR #{pr.number}: {pr.title}"
        )

        if success:
            self.pr_client.add_comment(
                pr.number, "Pull request has been automatically merged after approval."
            )
        else:
            self.pr_client.add_comment(
                pr.number, "Failed to automatically merge. Please check the PR status."
            )

        # Update tracking
        self.pr_tracking_storage.update_approval_check(pr.number)

    def _verify_build(self, pr: PullRequestInfo) -> bool:
        """Verify that the build passes for the PR branch."""
        try:
            repo_context = RepoContext(name=config.github_repo_name, branch=pr.head_branch)
            self.repository_client.checkout_branch(repo_context)

            # Run build check
            check_result = self.code_builder.check_commit(repo_context)

            if check_result.success:
                self.log.info(f"Build check passed for PR #{pr.number}")
                return True
            else:
                self.log.error(f"Build check failed for PR #{pr.number}: {check_result.stderr}")
                return False
        except Exception as e:
            self.log.error(f"Error running build check for PR #{pr.number}: {str(e)}")
            return False
