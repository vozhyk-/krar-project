from typing import NamedTuple

from structs.condition import Condition


class Observation(NamedTuple):
    condition: Condition
    begin_time: int
