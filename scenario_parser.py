from typing import List

from scenario import Scenario


class ScenarioParser:

    def __init__(self):
        pass

    def parse(self, file: str):
        with open(file) as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines]
        observation_lines, action_occurrence_lines = self.split_scenario(lines)

        return Scenario(observation_lines, action_occurrence_lines)

    def split_scenario(self, lines: List[str]):
        obs_idx = lines.index('OBS:')
        acs_idx = lines.index('ACS:')
        assert obs_idx < acs_idx
        observations = lines[obs_idx + 1:acs_idx]
        action_occurrences = lines[acs_idx + 1:]

        return (observations, action_occurrences)
