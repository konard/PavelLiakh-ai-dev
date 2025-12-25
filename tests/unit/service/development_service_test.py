import unittest
from unittest.mock import Mock, call

from src.app.domain.story import Story, NEW_STATE, DEVELOPMENT_STATE
from src.app.service.development_service import DevelopmentService, BRANCH_PREFIX
from src.infrastructure.ci.code_builder import BuildResult
from src.infrastructure.github.repository_client import RepoContext


class TestDevelopmentService(unittest.TestCase):
    def setUp(self):
        self.llm_client = Mock()
        self.git_repo_client = Mock()
        self.code_builder = Mock()
        self.planner_service = Mock()
        self.code_request_service = Mock()
        self.story_storage = Mock()
        self.log = Mock()

        self.service = DevelopmentService(
            self.llm_client,
            self.git_repo_client,
            self.code_builder,
            self.planner_service,
            self.code_request_service,
            self.story_storage,
            self.log,
        )

    def test_implement_calls_planner_and_code_request(self):
        story = Story(
            number=1,
            name="Test Story",
            description="Test",
            state=NEW_STATE,
            code_files={"test.py": "content"},
        )
        story.build_plan = ["Step 1"]

        self.code_builder.check_commit.return_value = BuildResult(success=True, stdout="Build OK")
        self.git_repo_client.open_pr.return_value = "https://github.com/test/test/pull/1"

        self.service.implement(story)

        self.planner_service.plan.assert_called_once_with(story)
        self.code_request_service.implement.assert_called_once_with(story)

    def test_implement_updates_story_state_to_development(self):
        story = Story(
            number=1,
            name="Test",
            state=NEW_STATE,
            code_files={"test.py": "content"},
        )
        story.build_plan = ["Step 1"]

        self.code_builder.check_commit.return_value = BuildResult(success=True)
        self.git_repo_client.open_pr.return_value = "https://pr.url"

        self.service.implement(story)

        assert story.state == DEVELOPMENT_STATE
        self.story_storage.save_story.assert_called()

    def test_implement_successful_build_pushes_and_opens_pr(self):
        story = Story(
            number=1,
            name="Test",
            state=NEW_STATE,
            code_files={"file.py": "code"},
        )
        story.build_plan = ["Step 1"]

        self.code_builder.check_commit.return_value = BuildResult(
            success=True, stdout="Build passed"
        )
        self.git_repo_client.open_pr.return_value = "https://github.com/repo/pull/1"

        self.service.implement(story)

        self.git_repo_client.push_changes.assert_called_once()
        self.git_repo_client.open_pr.assert_called_once()
        assert story.pr_link == "https://github.com/repo/pull/1"

    def test_implement_failed_build_does_not_push_or_open_pr(self):
        story = Story(
            number=1,
            name="Test",
            state=NEW_STATE,
            code_files={"file.py": "code"},
        )
        story.build_plan = ["Step 1"]

        self.code_builder.check_commit.return_value = BuildResult(
            success=False, stderr="Build failed", exit_code=1
        )

        self.service.implement(story)

        self.git_repo_client.push_changes.assert_not_called()
        self.git_repo_client.open_pr.assert_not_called()

    def test_get_repo_context_creates_correct_context(self):
        story = Story(number=123, name="Test")

        with unittest.mock.patch("src.app.service.development_service.config") as mock_config:
            mock_config.github_repo_name = "owner/repo"
            result = self.service._get_repo_context(story)

            assert isinstance(result, RepoContext)
            assert result.name == "owner/repo"
            assert result.branch == f"{BRANCH_PREFIX}123"

    def test_add_plan_to_repo(self):
        story = Story(number=1)
        story.build_plan = ["Step 1: Do X", "Step 2: Do Y"]
        repo_context = RepoContext(name="test/repo", branch="test-branch")

        self.service._add_plan_to_repo(story, repo_context)

        self.git_repo_client.checkout_branch.assert_called_once_with(repo_context)
        self.git_repo_client.patch_file.assert_called_once()
        call_args = self.git_repo_client.patch_file.call_args
        assert call_args[0][0] == repo_context
        assert "generated_plans/issue_1_plan.md" in call_args[0][1]
        assert "Step 1: Do X" in call_args[0][2]
        assert "Step 2: Do Y" in call_args[0][2]

    def test_add_generated_code_to_repo(self):
        story = Story(
            number=1, code_files={"src/main.py": "code1", "src/utils.py": "code2"}
        )
        repo_context = RepoContext(name="test/repo", branch="test-branch")

        self.service._add_generated_code_to_repo(story, repo_context)

        self.git_repo_client.checkout_branch.assert_called_once_with(repo_context)
        assert self.git_repo_client.patch_file.call_count == 2


if __name__ == "__main__":
    unittest.main()
