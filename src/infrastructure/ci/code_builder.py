import subprocess
from dataclasses import dataclass
from typing import Optional

from src.infrastructure.github.repository_client import RepoContext


@dataclass
class BuildResult:
    success: bool
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None


class CodeBuilder:
    def __init__(self, log, repository_client):
        self.log = log
        self.repository_client = repository_client

    def check_commit(self, repository_context: RepoContext) -> BuildResult:
        self.log.info(
            f"Building code: repo={repository_context.name}, branch={repository_context.branch}"
        )

        try:
            local_path = self.repository_client._get_local_path(repository_context.name)
            result = subprocess.run(
                ["bash", "build.sh"],
                cwd=local_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,  # don't raise exception, we handle it ourselves
            )

            if result.returncode == 0:
                self.log.info("Build succeeded")
                return BuildResult(success=True, stdout=result.stdout)
            else:
                self.log.error(f"Build failed with exit code {result.returncode}")
                return BuildResult(
                    success=False,
                    error="Build failed",
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                )

        except Exception as e:
            self.log.exception("Exception during build")
            return BuildResult(success=False, error=str(e))
