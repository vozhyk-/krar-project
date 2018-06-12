from typing import NamedTuple


class ActionOccurrence(NamedTuple):
    name: str
    begin_time: int
    duration: int
