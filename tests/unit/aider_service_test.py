"""Unit tests for AiderService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.app.service.aider_service import AiderService


class TestAiderService:
    """Test suite for AiderService."""

    def test_initialization_with_api_key(self):
        """Test AiderService initialization with API key."""
        log = Mock()
        api_key = "test-api-key"

        service = AiderService(log, api_key=api_key, model="gpt-4")

        assert service.api_key == api_key
        assert service.model == "gpt-4"
        assert service.log == log

    def test_initialization_without_api_key(self):
        """Test AiderService initialization without API key uses env var."""
        log = Mock()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-api-key"}):
            service = AiderService(log)
            assert service.api_key == "env-api-key"

    def test_initialization_no_api_key_logs_warning(self):
        """Test that missing API key logs a warning."""
        log = Mock()

        with patch.dict("os.environ", {}, clear=True):
            service = AiderService(log)
            log.warning.assert_called_once()
            assert "No API key" in log.warning.call_args[0][0]

    @patch("subprocess.run")
    def test_check_aider_available_success(self, mock_run):
        """Test checking aider availability when installed."""
        log = Mock()
        service = AiderService(log)

        mock_run.return_value = MagicMock(returncode=0, stdout="aider version 0.71.1")

        result = service.check_aider_available()

        assert result is True
        mock_run.assert_called_once()
        assert "aider" in mock_run.call_args[0][0]
        assert "--version" in mock_run.call_args[0][0]

    @patch("subprocess.run")
    def test_check_aider_available_not_installed(self, mock_run):
        """Test checking aider availability when not installed."""
        log = Mock()
        service = AiderService(log)

        mock_run.side_effect = FileNotFoundError("aider not found")

        result = service.check_aider_available()

        assert result is False

    @patch("subprocess.run")
    def test_analyze_code_success(self, mock_run):
        """Test successful code analysis."""
        log = Mock()
        service = AiderService(log, api_key="test-key")

        mock_run.return_value = MagicMock(
            returncode=0, stdout="Analysis result: This code does XYZ"
        )

        result = service.analyze_code(files=["test.py"], prompt="What does this code do?")

        assert "Analysis result" in result
        mock_run.assert_called_once()

        # Check command structure
        cmd = mock_run.call_args[0][0]
        assert "aider" in cmd
        assert "--model" in cmd
        assert "--message" in cmd
        assert "test.py" in cmd

    @patch("subprocess.run")
    def test_analyze_code_without_api_key_raises_error(self, mock_run):
        """Test that analyzing without API key raises ValueError."""
        log = Mock()
        service = AiderService(log, api_key=None)

        with pytest.raises(ValueError, match="API key is required"):
            service.analyze_code(files=["test.py"], prompt="test")

    @patch("subprocess.run")
    def test_analyze_code_timeout(self, mock_run):
        """Test code analysis with timeout."""
        log = Mock()
        service = AiderService(log, api_key="test-key")

        mock_run.side_effect = subprocess.TimeoutExpired("aider", 300)

        result = service.analyze_code(files=["test.py"], prompt="test")

        assert "timed out" in result.lower()

    @patch("subprocess.run")
    def test_edit_code_success(self, mock_run):
        """Test successful code editing."""
        log = Mock()
        service = AiderService(log, api_key="test-key")

        mock_run.return_value = MagicMock(returncode=0, stdout="Code edited successfully")

        result = service.edit_code(files=["test.py"], edit_instructions="Add docstring")

        assert result["success"] is True
        assert "successfully" in result["output"]
        mock_run.assert_called_once()

        # Check command structure
        cmd = mock_run.call_args[0][0]
        assert "aider" in cmd
        assert "--auto-commits" in cmd
        assert "test.py" in cmd

    @patch("subprocess.run")
    def test_edit_code_with_read_only_files(self, mock_run):
        """Test code editing with read-only context files."""
        log = Mock()
        service = AiderService(log, api_key="test-key")

        mock_run.return_value = MagicMock(returncode=0, stdout="Success")

        result = service.edit_code(
            files=["test.py"], edit_instructions="Update code", read_only_files=["context.py"]
        )

        assert result["success"] is True

        # Check that read-only file is included
        cmd = mock_run.call_args[0][0]
        assert "--read" in cmd
        assert "context.py" in cmd

    @patch("subprocess.run")
    def test_edit_code_failure(self, mock_run):
        """Test code editing failure."""
        log = Mock()
        service = AiderService(log, api_key="test-key")

        mock_run.return_value = MagicMock(returncode=1, stderr="Error: Invalid syntax")

        result = service.edit_code(files=["test.py"], edit_instructions="Bad instruction")

        assert result["success"] is False
        assert "Invalid syntax" in result["output"]

    @patch("subprocess.run")
    def test_get_repo_map(self, mock_run):
        """Test getting repository map."""
        log = Mock()
        service = AiderService(log)

        mock_run.return_value = MagicMock(
            returncode=0, stdout="Repository structure:\n- file1.py\n- file2.py"
        )

        result = service.get_repo_map()

        assert "Repository structure" in result
        assert "file1.py" in result

        # Check command
        cmd = mock_run.call_args[0][0]
        assert "aider" in cmd
        assert "--show-repo-map" in cmd

    @patch("subprocess.run")
    def test_get_repo_map_error(self, mock_run):
        """Test getting repository map with error."""
        log = Mock()
        service = AiderService(log)

        mock_run.return_value = MagicMock(returncode=1, stderr="Error: Not a git repository")

        result = service.get_repo_map()

        assert "Error" in result
        assert "git repository" in result
