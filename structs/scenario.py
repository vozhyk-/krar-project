from typing import List

from structs.observation import Observation
from structs.action_occurence import ActionOccurence


class Scenario:
    def __init__(self, observations: List[Observation], action_occurences: List[ActionOccurence]):
        self.observations = observations
        self.action_occurences = action_occurences
