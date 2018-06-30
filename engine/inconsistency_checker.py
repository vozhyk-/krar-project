from structs.scenario import Scenario
from structs.domain_description import DomainDescription
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import Not, And, Or
from structs.statements import Causes, Releases


class InconsistencyChecker:
    def __init__(self, domain_desc: DomainDescription, scen: Scenario):
        self.is_consistent = True
        self.sorted_actions = sorted(scen.action_occurrences, key=lambda action: action.begin_time)
        self.sorted_observations = sorted(scen.observations, key=lambda observation: observation.begin_time)
        self.domain_desc = domain_desc
        print('self.sorted_actions:', self.sorted_actions)
        print('self.sorted_observations:', self.sorted_observations)
        # Validate scenario
        self.check_for_overlapping_actions()
        self.check_for_contradictory_domain_desc()
        self.check_for_invalid_initial_state()

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

        # Uncomment the below if we want to remove actions with unsatisfiable preconditions
        # I don't think we have to care about this case
        '''
        # Check if at least ONE action precondition is satisfiable
        # empty precondition (A causes a) is always satisfiable
        # This fixes the following scenario: Shoot causes loaded if loaded & ~loaded
        # The precondition loaded & ~loaded is not satisfiable
        
        # TODO remove action with unsatisfiable precondition from DomainDescription?
        action_dict = dict()
        for i in range(len(self.domain_desc.statements)):
            statement = self.domain_desc.statements[i]
            # join preconditions of the same action by logical OR
            if isinstance(statement, (Causes, Releases)):
                if statement.condition is True:
                    break
                if statement.action not in action_dict:
                    action_dict[statement.action] = statement.condition.formula
                action_dict[statement.action] = Or(action_dict[statement.action], statement.condition.formula)

        for action_name, action_cond in action_dict.items():
            if not satisfiable(action_cond):
                print('precondition:', action_cond, 'is not satisfiable')
                self.is_consistent = False
                break
        '''
        # print('action_dict:', action_dict)
    def check_for_invalid_initial_state(self):
        initial_fluents = []
        if len(self.sorted_observations) > 0:
            # assume first observation is the initial description of fluents
            for fluent_name, fluent_value in satisfiable(self.sorted_observations[0].condition.formula).items():
                initial_fluents.append(fluent_name)

            for i in range(1, len(self.sorted_observations)):
                for fluent_name, fluent_val in satisfiable(self.sorted_observations[i].condition.formula).items():
                    if fluent_name not in initial_fluents:
                        self.is_consistent = False
                        print('Fluent:', fluent_name, 'was not defined in the initial state!')
