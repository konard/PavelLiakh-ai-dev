from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildResult:
    success: bool
    error: Optional[str] = None

class CodeBuilder:
    def check_commit(self, commit_hash) -> BuildResult:
        return BuildResult(True, None)
