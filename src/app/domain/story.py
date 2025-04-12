from dataclasses import dataclass


@dataclass
class Story:
    id: str  # DB ID
    name: str  # Display short name
    description: str  # Free-form text description of what need to be done
    comments: list[str]  # Comments
