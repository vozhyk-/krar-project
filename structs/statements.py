from typing import NamedTuple

from structs.condition import Condition


class Statement:
    pass

class EffectStatement(Statement, NamedTuple):
    action: str
    effect: Condition
    duration: int
    condition: Condition = True

class Causes(EffectStatement):
    pass

class Releases(EffectStatement):
    pass

class ImpossibleIf(Statement, NamedTuple):
    action: str
    condition: Condition

class ImpossibleAt(Statement, NamedTuple):
    action: str
    time: int
