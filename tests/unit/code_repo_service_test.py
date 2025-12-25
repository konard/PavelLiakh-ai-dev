import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock

from src.app.service.code_repo_service import CodeRepoServise


class TestCodeRepoService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.log = MagicMock()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_files_tree_with_simple_structure(self):
        """Test file tree generation with a simple directory structure"""
        # Create test directory structure
        test_root = Path(self.temp_dir)
        (test_root / "file1.py").write_text("print('hello')")
        (test_root / "file2.py").write_text("print('world')")
        (test_root / "subdir").mkdir()
        (test_root / "subdir" / "file3.py").write_text("print('test')")

        # Create service with test root
        service = CodeRepoServise(self.log, root_path=str(test_root))
        tree = service.get_files_tree()

        # Verify structure
        self.assertIn("file1.py", tree)
        self.assertIn("file2.py", tree)
        self.assertIn("subdir", tree)
        self.assertIn("file3.py", tree)

    def test_get_files_tree_ignores_common_patterns(self):
        """Test that common patterns like __pycache__ are ignored"""
        test_root = Path(self.temp_dir)
        (test_root / "file.py").write_text("print('hello')")
        (test_root / "__pycache__").mkdir()
        (test_root / "__pycache__" / "file.pyc").write_text("compiled")
        (test_root / ".git").mkdir()
        (test_root / ".git" / "config").write_text("git config")

        service = CodeRepoServise(self.log, root_path=str(test_root))
        tree = service.get_files_tree()

        # Verify ignored items are not in tree
        self.assertIn("file.py", tree)
        self.assertNotIn("__pycache__", tree)
        self.assertNotIn(".git", tree)
        self.assertNotIn(".pyc", tree)

    def test_get_files_tree_handles_nested_directories(self):
        """Test file tree generation with nested directories"""
        test_root = Path(self.temp_dir)
        (test_root / "level1").mkdir()
        (test_root / "level1" / "level2").mkdir()
        (test_root / "level1" / "level2" / "file.py").write_text("nested")

        service = CodeRepoServise(self.log, root_path=str(test_root))
        tree = service.get_files_tree()

        # Verify nested structure
        self.assertIn("level1", tree)
        self.assertIn("level2", tree)
        self.assertIn("file.py", tree)

    def test_get_files_tree_respects_max_depth(self):
        """Test that max_depth parameter is respected"""
        test_root = Path(self.temp_dir)
        # Create deeply nested structure
        current = test_root
        for i in range(10):
            current = current / f"level{i}"
            current.mkdir()
            (current / f"file{i}.py").write_text(f"level {i}")

        service = CodeRepoServise(self.log, root_path=str(test_root))
        tree = service.get_files_tree(max_depth=2)

        # Should contain early levels but not deep ones
        self.assertIn("level0", tree)
        self.assertIn("level1", tree)
        # level9 should not be included due to depth limit
        self.assertNotIn("level9", tree)

    def test_get_file_info_returns_content_and_spec(self):
        """Test get_file_info returns file content and specification"""
        test_root = Path(self.temp_dir)
        test_file = test_root / "test.py"
        test_content = """def hello(name: str) -> str:
    return f"Hello {name}"

class MyClass:
    def method(self):
        pass
"""
        test_file.write_text(test_content)

        service = CodeRepoServise(self.log, root_path=str(test_root))
        result = service.get_file_info("test.py")

        # Verify result is valid JSON
        import json

        result_data = json.loads(result)

        # Verify content is included
        self.assertEqual(result_data["content"], test_content)
        self.assertEqual(result_data["file_path"], "test.py")

        # Verify specification extracts function
        self.assertIn("hello", result_data["specification"])
        self.assertEqual(result_data["specification"]["hello"]["params"], "name: str")
        self.assertEqual(result_data["specification"]["hello"]["returns"], "str")

        # Verify specification extracts class
        self.assertIn("class_MyClass", result_data["specification"])

    def test_get_file_info_handles_non_python_files(self):
        """Test get_file_info handles non-Python files"""
        test_root = Path(self.temp_dir)
        test_file = test_root / "readme.txt"
        test_content = "This is a readme file"
        test_file.write_text(test_content)

        service = CodeRepoServise(self.log, root_path=str(test_root))
        result = service.get_file_info("readme.txt")

        import json

        result_data = json.loads(result)

        # Should have content but empty specification
        self.assertEqual(result_data["content"], test_content)
        self.assertEqual(result_data["specification"], {})

    def test_get_file_info_handles_missing_file(self):
        """Test get_file_info handles missing files gracefully"""
        test_root = Path(self.temp_dir)

        service = CodeRepoServise(self.log, root_path=str(test_root))
        result = service.get_file_info("nonexistent.py")

        import json

        result_data = json.loads(result)

        # Should return error
        self.assertIn("error", result_data)
        self.assertIn("File not found", result_data["error"])

    def test_detect_root_path_fallback(self):
        """Test that root path detection has a fallback"""
        service = CodeRepoServise(self.log)
        # Should not crash and should have a path
        self.assertIsNotNone(service.root_path)
        self.assertIsInstance(service.root_path, str)


if __name__ == "__main__":
    unittest.main()
