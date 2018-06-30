from structs.scenario import Scenario


class InconsistencyChecker:
    def __init__(self, scen: Scenario):
        self.is_consistent = True
        actions = sorted(scen.action_occurrences, key=lambda action: action.begin_time)
        for i in range(len(actions) - 1):
            if (actions[i].begin_time + actions[i].duration) > actions[i + 1].begin_time:
                self.is_consistent = False
                break
