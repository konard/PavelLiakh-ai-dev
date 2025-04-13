from dataclasses import dataclass
from typing import Optional

NEW_STATE = "NEW" # just arrived, not yet processed
PLANNING_STATE = "PLANNING" # in planning, not yet started
DEVELOPMENT_STATE = "DEVELOPMENT" # in development
DONE_STATE = "DONE" # done, ready for review
CANCELLED_STATE = "CANCELLED" # cancelled, not to be done

states = [NEW_STATE, PLANNING_STATE, DEVELOPMENT_STATE, DONE_STATE, CANCELLED_STATE]

@dataclass
class Story:
    _id: Optional[str] = None  # DB ID
    number: Optional[int] = None # Unique external identifier
    name: Optional[str] = None  # Brief title of the issue
    description: Optional[str] = None  # Free-form text description of what need to be done
    comments: Optional[list[str]] = None  # Comments
    state: Optional[str] = None # State of the issue. See `states` for possible values
