from structs.scenario import Scenario
from structs.domain_description import DomainDescription
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import Not, And, Or
from structs.statements import Causes, Releases
from engine.model import Model
from typing import List, Union, Tuple
from structs.statements import ImpossibleAt, ImpossibleIf, Statement
from structs.action_occurrence import ActionOccurrence
import sympy.parsing.sympy_parser as sympy_parser
from sympy.utilities.lambdify import lambdify


class InconsistencyChecker:
    def __init__(self, domain_desc: DomainDescription, scen: Scenario):
        self.is_consistent = True
        self.valid_scenario = None
        self.sorted_observations = sorted(scen.observations, key=lambda observation: observation.begin_time)
        self.sorted_actions = sorted(scen.action_occurrences, key=lambda action: action.begin_time)
        self.domain_desc = domain_desc
        # Validate scenario
        self.check_for_overlapping_actions()
        self.check_for_contradictory_domain_desc()
        self.check_for_invalid_initial_state()
        if self.is_consistent:
            self.valid_scenario = Scenario(self.sorted_observations, self.sorted_actions)
            print('self.valid_scenario.action_occurrences', self.valid_scenario.action_occurrences)
            print('self.valid_scenario.observations:', self.valid_scenario.observations)
        self.actions_at_time_t = dict()  # Maps time: int -> action_occurrence
        # Observations from domain description
        self.observations_at_time_t = dict()  # Maps time: int -> List[Observation]
        # ImpossibleIf statements
        self.action_formula_constraints = list()  # List[ImpossibleIf]
        # ImpossibleAt statements
        self.action_time_constraints_at_time_t = dict()  # Maps time: int -> List[str] (List of action names not executable at t)
        self.last_time = self.sorted_actions[-1].begin_time + self.sorted_actions[-1].duration + 1
        self.initialize_data()
        # print(self.actions_at_time_t)
        # print(self.observations_at_time_t)
        # print(self.action_formula_constraints)
        # print(self.action_time_constraints_at_time_t)

    def initialize_data(self):
        self.action_formula_constraints = [fc for fc in self.domain_desc.statements if
                                           isinstance(fc,
                                                      ImpossibleIf)]
        for t in range(self.last_time):
            action_at_time_t = next((action for action in self.sorted_actions if action.begin_time == t),
                                    None)
            if action_at_time_t is not None:
                self.actions_at_time_t[t] = action_at_time_t
            observations_at_time_t = [ob for ob in self.sorted_observations if
                                      ob.begin_time == t]
            impossible_at_action_names = [ac.action for ac in self.domain_desc.statements if
                                          isinstance(ac, ImpossibleAt) and ac.time == t]  # This applies to all models
            if len(observations_at_time_t) > 0:
                self.observations_at_time_t[t] = []
                for ob in observations_at_time_t:
                    self.observations_at_time_t[t].append(ob)
            if len(impossible_at_action_names) > 0:
                self.action_time_constraints_at_time_t[t] = []
                for action_name in impossible_at_action_names:
                    self.action_time_constraints_at_time_t[t].append(action_name)

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

    def remove_duplicate_models(self, models: List[Model]) -> List[Model]:
        new_list = []
        for m in models:
            if m not in new_list:
                new_list.append(m)
            else:
                pass
                # print('Model:\n', m, '\n Is already in the list!')
        return new_list

    # Returns
    # Second element of tuple is valid action to be executed (if it exists)
    # Third element is the statement associated with the action returned as the 2nd argument
    def validate_model(self, model: Model, time: int) -> Tuple[bool, Union[ActionOccurrence, None],  Union[Statement, None]]:
        """
        Firstly we find an action and its correlated statement that are affecting the model at time "time"
        If an action is found, then it is validated against ImpossibleAt/ImpossibleIf statements
        :param model: The model to be validated
        :param time: The time at which we check/validate the model
        :return: A tuple of 3 elements, first is a bool that says whether or not model is valid
        second is the action that is affecting the model passed into the method, and the third is the EffectStatement
        that is correlated with the action
        """
        current_statement = None
        current_action = None
        for t in self.actions_at_time_t.keys():
            action = self.actions_at_time_t[t]
            for statement in self.domain_desc.statements:
                if isinstance(statement, (Causes, Releases)) and statement.action == action.name:
                    if action.begin_time + statement.duration == time:
                        # We found what statement is happening now
                        current_statement = statement
                        current_action = action
        # If no action is affecting us now, assume model is valid
        if current_action is None or current_statement is None:
            return True, None, None

        # Check ImpossibleAt
        if current_action.begin_time in self.action_time_constraints_at_time_t:
            if current_action.name in self.action_time_constraints_at_time_t[current_action.begin_time]:
                print('action:', current_action, 'violates impossible_at at time:', current_action.begin_time)
                return False, None, None
        # Below we validate the action that was found against ImpossibleAt/ImpossibleIf
        current_fluents = model.fluent_history[current_action.begin_time]
        fluent_symbol_dict = dict()  # SympySymbol -> bool
        # Convert state of fluents to sympy dict
        # https://stackoverflow.com/questions/42024034/evaluate-sympy-boolean-expression-in-python
        for fluent in current_fluents:
            fluent_symbol_dict[sympy_parser.parse_expr(fluent.name)] = fluent.value
        expr = tuple(fluent_symbol_dict.keys())
        expr_values = tuple(fluent_symbol_dict.values())
        # Check ImpossibleIf statements
        for impossible_if in self.action_formula_constraints:
            if current_action.name == impossible_if.action:
                # Using the lambdify() method, we can evaluate a boolean formula given state of boolean variables
                # There is no "eval()" method in sympy for solving boolean formulas
                f = lambdify(expr, impossible_if.condition.formula, modules={'And': all, 'Or': any})
                evaluation = f(*expr_values)
                print('(ImpossibleIf) Expression:', expr, 'given values:', expr_values, 'in the formula:',
                      impossible_if.condition.formula,
                      'was evaluated to:',
                      evaluation, 'for action:', action.name, 'at time:', time)
                # Invalid model, so we don't even try to find an action for this time
                if evaluation:
                    print('action:', action, 'violates impossible_if:', impossible_if, 'at time:', time, 'expr:',
                          expr)
                    return False, None, None
        return True, current_action, current_statement

    def remove_bad_observations(self, models: List[Model], time: int):
        """
        This method is executed after forking new models. 
        It may happen that a newly forked model violates an observation that we had at a given time,
        if so we must remove it.
        :param models: The list of models that will be checked for invalid state of fluents
        :param time: The time at which the observations will be checked
        :return: None
        """
        for i in range(len(models) - 1, -1, -1):
            current_fluents = models[i].fluent_history[time]
            fluent_symbol_dict = dict()  # SympySymbol -> bool
            # Convert state of fluents to sympy dict
            # https://stackoverflow.com/questions/42024034/evaluate-sympy-boolean-expression-in-python
            for fluent in current_fluents:
                fluent_symbol_dict[sympy_parser.parse_expr(fluent.name)] = fluent.value
            expr = tuple(fluent_symbol_dict.keys())
            expr_values = tuple(fluent_symbol_dict.values())
            if time in self.observations_at_time_t:
                for obs in self.observations_at_time_t[time]:
                    # https://stackoverflow.com/questions/42045906/typeerror-return-arrays-must-be-of-arraytype-using-lambdify-of-sympy-in-python
                    f = lambdify(expr, obs.condition.formula, modules={'And': all, 'Or': any})
                    evaluation = f(*expr_values)
                    print('(Observations) Expression:', expr, 'given values:', expr_values, 'in the formula:',
                          obs.condition.formula, 'was evaluated to:',
                          evaluation, 'at time:', time)
                    # Invalid model, so we don't even try to find an action for this time
                    if not evaluation:
                        models.remove(models[i])
