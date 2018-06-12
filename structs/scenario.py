from typing import NamedTuple, List

from structs.observation import Observation
from structs.action_occurrence import ActionOccurrence


class Scenario(NamedTuple):
    observations: List[Observation]
    action_occurrences: List[ActionOccurrence]
