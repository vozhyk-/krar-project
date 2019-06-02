from typing import NamedTuple

from structs.condition import Condition


class Statement:
    pass


class EffectStatement(Statement, NamedTuple):
    action: str
    effect: Condition
    duration: int = 1
    condition: Condition = True
    agent: str = 'nobody'


class Causes(EffectStatement):
    pass


class Releases(EffectStatement):
    pass


class ImpossibleIf(Statement, NamedTuple):
    action: str
    condition: Condition


# TODO REMOVE
class ImpossibleAt(Statement, NamedTuple):
    action: str
    time: int


class ImpossibleBy(Statement, NamedTuple):
    action: str
    agent: str


class Triggers(Statement, NamedTuple):
    condition: Condition
    action: str
    agent: str
