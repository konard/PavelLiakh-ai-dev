from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Prompt:
    task: str
    role: Optional[str]
    context: list[str] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    output: Optional[str] = None

    def to_str(self) -> str:
        def strip(strs: list[str]) -> list[str]:
            return [s.strip() for s in strs]

        """Convert Prompt instance to a formatted string."""
        parts = []
        if self.role:
            parts.append(f"Role: {self.role}")
        parts.append(f"Task: {self.task}")
        if self.instructions:
            parts.append(f"Instructions:\n-" + "\n-".join(strip(self.instructions)))
        if self.context:
            parts.append(f"Context:\n-" + "\n-".join(strip(self.context)))
        if self.examples:
            parts.append(f"Examples:\n-" + "\n-".join(strip(self.examples)))
        if self.output:
            parts.append(f"Output: {self.output}")

        return "\n\n".join(parts)

    @staticmethod
    def from_dict(data: dict) -> "Prompt":
        """Create a Prompt instance from a dictionary."""
        return Prompt(
            task=data.get("task", ""),
            role=data.get("role"),
            context=data.get("context", []),
            instructions=data.get("instructions", []),
            examples=data.get("examples", []),
            output=data.get("output"),
        )
