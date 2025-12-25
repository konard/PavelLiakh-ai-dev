"""Service for integrating aider AI pair programming tool for code analysis and editing."""

import os
import subprocess
import tempfile
from typing import Optional, List
from pathlib import Path


class AiderService:
    """
    Service that integrates aider tool for AI-powered code analysis and editing.

    Aider is an AI pair programming tool that can analyze and modify code using LLMs.
    Since aider is not available as a library (as per https://github.com/Aider-AI/aider/issues/1831),
    this service wraps aider's CLI functionality to provide programmatic access.
    """

    def __init__(self, log, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the AiderService.

        Args:
            log: Logger instance
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use with aider (default: gpt-4o)
        """
        self.log = log
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            self.log.warning(
                "No API key provided for AiderService. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

    def analyze_code(self, files: List[str], prompt: str, repo_path: Optional[str] = None) -> str:
        """
        Use aider to analyze code files with a given prompt.

        Args:
            files: List of file paths to analyze
            prompt: Analysis prompt/question for aider
            repo_path: Optional repository path (defaults to current directory)

        Returns:
            Aider's analysis response as a string
        """
        if not self.api_key:
            raise ValueError("API key is required to use aider")

        self.log.info(f"Using aider to analyze {len(files)} files with prompt: {prompt[:100]}...")

        # Use aider's --message flag for one-shot analysis
        cmd = [
            "aider",
            "--model",
            self.model,
            "--message",
            prompt,
            "--no-auto-commits",  # Don't auto-commit changes
            "--yes",  # Auto-confirm prompts
        ]

        # Add files to analyze
        cmd.extend(files)

        env = os.environ.copy()
        env["OPENAI_API_KEY"] = self.api_key

        cwd = repo_path or os.getcwd()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                self.log.error(f"Aider analysis failed: {result.stderr}")
                return f"Error: {result.stderr}"

            self.log.info("Aider analysis completed successfully")
            return result.stdout

        except subprocess.TimeoutExpired:
            self.log.error("Aider analysis timed out after 5 minutes")
            return "Error: Analysis timed out"
        except Exception as e:
            self.log.error(f"Aider analysis failed with exception: {e}")
            return f"Error: {str(e)}"

    def edit_code(
        self,
        files: List[str],
        edit_instructions: str,
        repo_path: Optional[str] = None,
        read_only_files: Optional[List[str]] = None,
    ) -> dict:
        """
        Use aider to edit code files based on instructions.

        Args:
            files: List of file paths to edit
            edit_instructions: Instructions for what changes to make
            repo_path: Optional repository path (defaults to current directory)
            read_only_files: Optional list of files to add as read-only context

        Returns:
            Dictionary with 'success' boolean and 'output' string
        """
        if not self.api_key:
            raise ValueError("API key is required to use aider")

        self.log.info(
            f"Using aider to edit {len(files)} files with instructions: "
            f"{edit_instructions[:100]}..."
        )

        cmd = [
            "aider",
            "--model",
            self.model,
            "--message",
            edit_instructions,
            "--auto-commits",  # Auto-commit changes
            "--yes",  # Auto-confirm prompts
        ]

        # Add files to edit
        cmd.extend(files)

        # Add read-only files if provided
        if read_only_files:
            for ro_file in read_only_files:
                cmd.extend(["--read", ro_file])

        env = os.environ.copy()
        env["OPENAI_API_KEY"] = self.api_key

        cwd = repo_path or os.getcwd()

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for edits
            )

            success = result.returncode == 0

            if not success:
                self.log.error(f"Aider edit failed: {result.stderr}")
            else:
                self.log.info("Aider edit completed successfully")

            return {"success": success, "output": result.stdout if success else result.stderr}

        except subprocess.TimeoutExpired:
            self.log.error("Aider edit timed out after 10 minutes")
            return {"success": False, "output": "Error: Edit timed out"}
        except Exception as e:
            self.log.error(f"Aider edit failed with exception: {e}")
            return {"success": False, "output": f"Error: {str(e)}"}

    def get_repo_map(self, repo_path: Optional[str] = None) -> str:
        """
        Get aider's repository map for better code understanding.

        Args:
            repo_path: Optional repository path (defaults to current directory)

        Returns:
            Repository map as a string
        """
        self.log.info("Generating repository map with aider")

        cmd = [
            "aider",
            "--show-repo-map",
        ]

        cwd = repo_path or os.getcwd()

        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                self.log.error(f"Failed to get repo map: {result.stderr}")
                return f"Error: {result.stderr}"

            return result.stdout

        except Exception as e:
            self.log.error(f"Failed to get repo map: {e}")
            return f"Error: {str(e)}"

    def check_aider_available(self) -> bool:
        """
        Check if aider is installed and available.

        Returns:
            True if aider is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["aider", "--version"], capture_output=True, text=True, timeout=10
            )
            available = result.returncode == 0

            if available:
                self.log.info(f"Aider is available: {result.stdout.strip()}")
            else:
                self.log.warning("Aider is not available")

            return available

        except Exception as e:
            self.log.warning(f"Aider is not available: {e}")
            return False
