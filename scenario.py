from observation import Observation
from action_occurence import ActionOccurence
from typing import List

class Scenario:
    def __init__(self, observations: List[Observation], action_occurences: List[ActionOccurence]):
        self.observations = observations
        self.action_occurences = action_occurences