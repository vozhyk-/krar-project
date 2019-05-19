from typing import NamedTuple


class ActionOccurrence(NamedTuple):
    name: str
    begin_time: int
    agent: str
    duration: int = 1  # Keep for compatibility reasons?
