from typing import NamedTuple

from structs.condition import Condition


class Statement:
    pass

class Causes(Statement, NamedTuple):
    action: str
    effect: Condition
    duration: int

class Releases(Statement):
    pass

class ImpossibleIf(Statement, NamedTuple):
    action: str
    condition: Condition

class ImpossibleAt(Statement, NamedTuple):
    action: str
    time: int
