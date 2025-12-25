import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.infrastructure.ci.code_builder import CodeBuilder, BuildResult
from src.infrastructure.github.repository_client import RepoContext


class TestCodeBuilder(unittest.TestCase):
    def setUp(self):
        self.log = Mock()
        self.repository_client = Mock()
        self.code_builder = CodeBuilder(self.log, self.repository_client)

    @patch("src.infrastructure.ci.code_builder.subprocess.run")
    def test_check_commit_successful_build(self, mock_run):
        repo_context = RepoContext(name="test/repo", branch="test-branch")
        self.repository_client._get_local_path.return_value = Path("/tmp/test-repo")

        mock_run.return_value = Mock(returncode=0, stdout="Build successful", stderr="")

        result = self.code_builder.check_commit(repo_context)

        assert result.success is True
        assert result.stdout == "Build successful"
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["bash", "build.sh"]
        assert call_args[1]["cwd"] == Path("/tmp/test-repo")

    @patch("src.infrastructure.ci.code_builder.subprocess.run")
    def test_check_commit_failed_build(self, mock_run):
        repo_context = RepoContext(name="test/repo", branch="test-branch")
        self.repository_client._get_local_path.return_value = Path("/tmp/test-repo")

        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="Build failed: syntax error"
        )

        result = self.code_builder.check_commit(repo_context)

        assert result.success is False
        assert result.error == "Build failed"
        assert result.stderr == "Build failed: syntax error"
        assert result.exit_code == 1

    @patch("src.infrastructure.ci.code_builder.subprocess.run")
    def test_check_commit_exception_handling(self, mock_run):
        repo_context = RepoContext(name="test/repo", branch="test-branch")
        self.repository_client._get_local_path.return_value = Path("/tmp/test-repo")

        mock_run.side_effect = Exception("Subprocess error")

        result = self.code_builder.check_commit(repo_context)

        assert result.success is False
        assert "Subprocess error" in result.error

    @patch("src.infrastructure.ci.code_builder.subprocess.run")
    def test_check_commit_logs_correctly(self, mock_run):
        repo_context = RepoContext(name="owner/repo", branch="feature-branch")
        self.repository_client._get_local_path.return_value = Path("/tmp/repo")

        mock_run.return_value = Mock(returncode=0, stdout="OK", stderr="")

        self.code_builder.check_commit(repo_context)

        self.log.info.assert_called()
        log_calls = [call[0][0] for call in self.log.info.call_args_list]
        assert any("owner/repo" in call and "feature-branch" in call for call in log_calls)


class TestBuildResult(unittest.TestCase):
    def test_build_result_success(self):
        result = BuildResult(success=True, stdout="All tests passed")

        assert result.success is True
        assert result.stdout == "All tests passed"
        assert result.error is None
        assert result.stderr is None
        assert result.exit_code is None

    def test_build_result_failure(self):
        result = BuildResult(
            success=False,
            error="Build failed",
            stderr="Error details",
            exit_code=1,
        )

        assert result.success is False
        assert result.error == "Build failed"
        assert result.stderr == "Error details"
        assert result.exit_code == 1


if __name__ == "__main__":
    unittest.main()
