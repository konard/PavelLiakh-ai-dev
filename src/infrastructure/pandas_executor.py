import contextlib
import io
import traceback


class PandasScriptExecutor:
    @staticmethod
    def execute(script: str) -> tuple[str, str]:  # Return a tuple of (stdout, stderr)
        """Executes a script and captures stdout and stderr."""

        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(
                stderr_buffer
            ):
                exec(script.replace("```python", "").replace("```", ""))
            stdout = stdout_buffer.getvalue().strip()
            stderr = stderr_buffer.getvalue().strip()

        except Exception:
            stdout = stdout_buffer.getvalue().strip()
            stderr = f"MyError:\n{traceback.format_exc().strip()}"

        return stdout, stderr
