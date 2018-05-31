from scenario import Scenario


class ScenarioParser:

    def __init__(self):
        pass

    def parse(self, file: str):
        content = []
        with open(file) as f:
            content = f.readlines()
        content = [x.strip().split(' ') for x in content]
        obs_idx = content.index(['OBS:'])
        acs_idx = content.index(['ACS:'])
        assert obs_idx < acs_idx
        observations = content[obs_idx + 1:acs_idx]
        action_occurrences = content[acs_idx + 1:]

        return Scenario(observations, action_occurrences)
