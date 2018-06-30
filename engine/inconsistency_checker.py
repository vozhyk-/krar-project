from structs.scenario import Scenario
from structs.domain_description import DomainDescription
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import Not, And, Or
from structs.statements import Causes, Releases


class InconsistencyChecker:
    def __init__(self, domain_desc: DomainDescription, scen: Scenario,):
        self.is_consistent = True
        self.sorted_actions = sorted(scen.action_occurrences, key=lambda action: action.begin_time)
        self.sorted_observations = sorted(scen.observations, key=lambda observation: observation.begin_time)
        self.domain_desc = domain_desc
        print('self.sorted_actions:', self.sorted_actions)
        print('self.sorted_observations:', self.sorted_observations)
        # Validate scenario
        self.check_for_overlapping_actions()
        self.check_for_contradictory_domain_desc()

    def check_for_overlapping_actions(self):
        for i in range(len(self.sorted_actions) - 1):
            if (self.sorted_actions[i].begin_time +
                    self.sorted_actions[i].duration) > self.sorted_actions[i + 1].begin_time:
                print('Overlapping action found, action name:', self.sorted_actions[i].name, 'overlaps with action:',
                      self.sorted_actions[i + 1].name)
                self.is_consistent = False
                break

    def check_for_contradictory_domain_desc(self):
        action_dict = dict()  # Maps action name -> Conditions joined by and
        for i in range(len(self.domain_desc.statements)):
            statement = self.domain_desc.statements[i]
            # print(statement)
            # join action with its causes/releases effect
            if isinstance(statement, (Causes, Releases)):
                if statement.action not in action_dict:
                    action_dict[statement.action] = statement.effect.formula
                action_dict[statement.action] = And(action_dict[statement.action], statement.effect.formula)

        for action_name, action_cond in action_dict.items():
            if not satisfiable(action_cond):
                print('action_cond:', action_cond, 'is not satisfiable')
                self.is_consistent = False
                break
        # print('action_dict:', action_dict)
