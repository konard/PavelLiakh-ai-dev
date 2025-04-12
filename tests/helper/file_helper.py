from pathlib import Path
import json


def get_file_path(file_name: str, test_resources_folder: str = "tests/integration/") -> Path:
    search_paths = [
        Path(file_name),  # Direct path
        Path(test_resources_folder, file_name),  # Test resources folder
        Path("files", file_name),  # Tests folder
        Path("tests", file_name),  # Tests folder
        Path("tests/helper/", file_name),  # Helper folder
        Path("tests/integration/", file_name),  # Integ test folder
        Path("tests/unit/", file_name),  # Unit test folder
    ]

    # Check each path in sequence
    for path in search_paths:
        if path.exists():
            return path.absolute()

    # If no path was found
    raise FileNotFoundError(
        f"File {file_name} not found in any of: {[str(p) for p in search_paths]}"
    )


def get_file_content(file_name: str, test_resources_folder: str = "tests/integration/") -> str:
    file_path = get_file_path(file_name, test_resources_folder)
    return file_path.read_text()


def get_json(file_name: str, test_resources_folder: str = "tests/integration/") -> dict:
    content = get_file_content(file_name, test_resources_folder)
    return json.loads(content)
