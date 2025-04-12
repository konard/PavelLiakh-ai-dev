import unittest
from typing import List

from src.ioc import pandas_executor
from tests.helper.assert_helper import assert_equals
from tests.helper.file_helper import get_file_content, get_file_path


def remove_pandas_executor_line(text: str) -> str:
    """Remove any line containing 'pandas_executor.py' from the text."""
    lines: List[str] = text.splitlines()
    return "\n".join(line for line in lines if "pandas_executor.py" not in line)


class TestPandasExecutor(unittest.TestCase):
    def test_working_script(self):
        # given
        example_file_path = get_file_path("files/example.csv")
        working_script = get_file_content("files/working_script.txt").replace(
            "%X_PATH%", str(example_file_path)
        )

        # when
        out, err = pandas_executor.execute(working_script)

        # then
        assert not err
        expected_out = get_file_content("files/expected_out.txt")
        assert_equals(expected_out, out)

    def test_failing_script(self):
        # given
        example_file_path = get_file_path("files/example.csv")
        failing_script = get_file_content("files/failing_script.txt").replace(
            "%X_PATH%", str(example_file_path)
        )

        # when
        out, err = pandas_executor.execute(failing_script)

        # then
        assert err
        assert_equals("hello from the failing script", out)
        expected_err = get_file_content("files/expected_err.txt")
        assert_equals(remove_pandas_executor_line(expected_err), remove_pandas_executor_line(err))


if __name__ == "__main__":
    unittest.main()
