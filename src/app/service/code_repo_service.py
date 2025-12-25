import os
import json
from pathlib import Path
from typing import Optional


class CodeRepoServise:
    def __init__(self, log, root_path: Optional[str] = None):
        self.log = log
        self.root_path = root_path or self._detect_root_path()

    def _detect_root_path(self) -> str:
        """Detect the root path of the repository by looking for src directory"""
        current = Path(__file__).resolve()
        # Navigate up from this file's location to find src directory
        while current.parent != current:
            if (current / "src").exists():
                return str(current / "src")
            current = current.parent
        # Fallback to the directory containing this file
        return str(Path(__file__).parent.parent.parent)

    def get_files_tree(self, max_depth: int = 5) -> str:
        """
        Generate a tree representation of the repository structure.

        Args:
            max_depth: Maximum directory depth to traverse (default: 5)

        Returns:
            String representation of the file tree in tree-like format
        """
        self.log.info(f"Generating file tree for path: {self.root_path}")

        root_dir = Path(self.root_path)
        if not root_dir.exists():
            self.log.error(f"Root path does not exist: {self.root_path}")
            return f"Error: Path {self.root_path} does not exist"

        # Directories and files to ignore
        ignore_patterns = {
            "__pycache__",
            ".pytest_cache",
            ".git",
            ".idea",
            ".vscode",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
            "dist",
            "build",
            ".tox",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
            "test_report",
            ".coverage",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
        }

        def should_ignore(path: Path) -> bool:
            """Check if path should be ignored"""
            name = path.name
            # Check exact matches
            if name in ignore_patterns:
                return True
            # Check patterns with wildcards
            for pattern in ignore_patterns:
                if "*" in pattern:
                    if pattern.startswith("*"):
                        if name.endswith(pattern[1:]):
                            return True
                    if pattern.endswith("*"):
                        if name.startswith(pattern[:-1]):
                            return True
            return False

        def build_tree(directory: Path, prefix: str = "", depth: int = 0) -> list[str]:
            """Recursively build tree structure"""
            if depth > max_depth:
                return []

            lines = []
            try:
                # Get all entries and separate into directories and files
                entries = sorted(
                    directory.iterdir(), key=lambda x: (not x.is_dir(), x.name)
                )
                # Filter out ignored items
                entries = [e for e in entries if not should_ignore(e)]

                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1

                    # Choose the right connector
                    if is_last:
                        connector = "\\---" if entry.is_dir() else "    "
                        extension = "    "
                    else:
                        connector = "+---" if entry.is_dir() else "|   "
                        extension = "|   "

                    # Add current entry
                    if entry.is_dir():
                        lines.append(f"{prefix}{connector}{entry.name}")
                        # Recursively add subdirectory contents
                        sub_lines = build_tree(entry, prefix + extension, depth + 1)
                        lines.extend(sub_lines)
                    else:
                        lines.append(f"{prefix}{connector}{entry.name}")

            except PermissionError:
                self.log.warning(f"Permission denied: {directory}")

            return lines

        # Start building the tree
        tree_lines = [f"{root_dir.name}:"]
        tree_lines.extend(build_tree(root_dir))

        result = "\n".join(tree_lines)
        self.log.info(f"Generated file tree with {len(tree_lines)} lines")
        return result

    def get_file_info(self, repo_file_path: str) -> str:
        """
        Get information about a specific file including content and basic structure.

        Args:
            repo_file_path: Relative path to the file from repository root

        Returns:
            JSON string containing file content and specification
        """
        self.log.info(f"Getting file info for: {repo_file_path}")

        full_path = Path(self.root_path) / repo_file_path

        if not full_path.exists():
            error_result = {
                "error": f"File not found: {repo_file_path}",
                "content": "",
                "specification": {},
            }
            return json.dumps(error_result, indent=2)

        try:
            # Read file content
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic specification extraction for Python files
            specification = {}
            if full_path.suffix == ".py":
                # Simple extraction of function and class definitions
                import re

                # Find function definitions
                func_pattern = r"^\s*def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*(.+?))?:"
                for match in re.finditer(func_pattern, content, re.MULTILINE):
                    func_name = match.group(1)
                    params = match.group(2).strip()
                    returns = match.group(3).strip() if match.group(3) else "None"
                    specification[func_name] = {"params": params, "returns": returns}

                # Find class definitions
                class_pattern = r"^\s*class\s+(\w+)(?:\((.+?)\))?:"
                for match in re.finditer(class_pattern, content, re.MULTILINE):
                    class_name = match.group(1)
                    bases = match.group(2).strip() if match.group(2) else ""
                    specification[f"class_{class_name}"] = {
                        "type": "class",
                        "bases": bases,
                    }

            result = {
                "file_path": repo_file_path,
                "content": content,
                "specification": specification,
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            self.log.error(f"Error reading file {repo_file_path}: {e}")
            error_result = {"error": str(e), "content": "", "specification": {}}
            return json.dumps(error_result, indent=2)
