from typing import List

from structs.observation import Observation
from structs.action_occurrence import ActionOccurrence


class Scenario:
    def __init__(self, observations: List[Observation], action_occurrences: List[ActionOccurrence]):
        self.observations = observations
        self.action_occurrences = action_occurrences
