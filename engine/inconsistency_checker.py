from structs.scenario import Scenario
from structs.domain_description import DomainDescription
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import Not, And, Or
from structs.statements import Causes, Releases
from engine.model import Model
from typing import List, Union, Tuple, Dict, Optional
from structs.statements import ImpossibleAt, ImpossibleIf, ImpossibleBy, Statement, EffectStatement
from structs.action_occurrence import ActionOccurrence
import sympy.parsing.sympy_parser as sympy_parser
from sympy.utilities.lambdify import lambdify
from sympy.logic import boolalg
from sympy import Symbol
from structs.condition import Condition


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
            # print('self.valid_scenario.action_occurrences', self.valid_scenario.action_occurrences)
            # print('self.valid_scenario.observations:', self.valid_scenario.observations)
        self.actions_at_time_t = dict()  # Maps time: int -> action_occurrence
        # Observations from domain description
        self.observations_at_time_t = dict()  # Maps time: int -> List[Observation]
        # ImpossibleIf statements
        self.action_formula_constraints = list()  # List[ImpossibleIf]
        self.impossible_by_statements = []  # List[ImpossibleBy]
        # ImpossibleAt statements
        self.action_time_constraints_at_time_t = dict()  # Maps time: int -> List[str] (List of action names not executable at t)
        self.last_time = self.sorted_actions[-1].begin_time + self.sorted_actions[-1].duration + 1
        self.joined_statements = dict()  # Stores the joined releases/causes statements that have same name, time, and duration
        self.initialize_data()
        # print('self.joined_statements:\n', self.joined_statements)
        # print(self.actions_at_time_t)
        # print(self.observations_at_time_t)
        # print(self.action_formula_constraints)
        # print(self.action_time_constraints_at_time_t)

    def initialize_data(self):
        self.action_formula_constraints = [fc for fc in self.domain_desc.statements if
                                           isinstance(fc,
                                                      ImpossibleIf)]
        self.impossible_by_statements = [x for x in self.domain_desc.statements if
                                         isinstance(x,
                                                    ImpossibleBy)]
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

        for i in range(len(self.domain_desc.statements)):
            statement = self.domain_desc.statements[i]
            # print(statement)
            # join action with its causes/releases effect
            if isinstance(statement, (Causes, Releases)):
                if statement.action not in self.joined_statements:
                    self.joined_statements[statement.action] = [statement]
                else:
                    for j in range(len(self.joined_statements[statement.action])):
                        if self.joined_statements[statement.action][j].duration == statement.duration and \
                                self.joined_statements[statement.action][j].condition == statement.condition:
                            if isinstance(statement, Causes) and isinstance(self.joined_statements[statement.action][j],
                                                                            Causes):
                                if self.joined_statements[statement.action][j].agent == statement.agent:
                                    self.joined_statements[statement.action][j] = self.join_statement_by_and(
                                        self.joined_statements[statement.action][j], statement, True)
                                else:
                                    self.joined_statements[statement.action].append(statement)
                            elif isinstance(statement, Releases) and isinstance(
                                    self.joined_statements[statement.action][j], Releases):
                                if self.joined_statements[statement.action][j].agent == statement.agent:
                                    self.joined_statements[statement.action][j] = self.create_tautology_from_statements(
                                        self.joined_statements[statement.action][j], statement)
                                else:
                                    self.joined_statements[statement.action].append(statement)
                        else:
                            self.joined_statements[statement.action].append(statement)

    def check_for_overlapping_actions(self):
        for i in range(len(self.sorted_actions) - 1):
            if (self.sorted_actions[i].begin_time + self.sorted_actions[i].duration) > self.sorted_actions[
                i + 1].begin_time:
                # print('Overlapping action found, action name:', self.sorted_actions[i].name, 'overlaps with action:',
                #       self.sorted_actions[i + 1].name)
                self.is_consistent = False
                break

    # TODO change this method, right now it ignores action durations
    # TODO and whether or not statements are Releases or Causes statements, we need to rework it
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
                # print('action_cond:', action_cond, 'is not satisfiable')
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
            if not satisfiable(self.sorted_observations[0].condition.formula):
                for fluent_name, fluent_value in satisfiable(self.sorted_observations[0].condition.formula).items():
                    initial_fluents.append(fluent_name)

            if not satisfiable(self.sorted_observations[0].condition.formula):
                for i in range(1, len(self.sorted_observations)):
                    for fluent_name, fluent_val in satisfiable(self.sorted_observations[i].condition.formula).items():
                        if fluent_name not in initial_fluents:
                            self.is_consistent = False
                        # print('Fluent:', fluent_name, 'was not defined in the initial state!')

    def remove_duplicate_models(self, models: List[Model]) -> List[Model]:
        new_list = []
        for m in models:
            if m not in new_list:
                new_list.append(m)
            else:
                pass
                # print('Model:\n', m, '\n Is already in the list!')
        return new_list

    def validate_model(self, model: Model, time: int) -> Tuple[
        bool, Optional[ActionOccurrence], Optional[EffectStatement], str]:
        """
        Firstly we find an action,
        then we look in the domain description for Releases/Causes statements that have an effect at this specific time.
        We then join releases/causes statements together into 1 big Releases statement and 1 big Causes statement
        Then we return the statements that are CAUSED at this time, and the statements that are RELEASED at this time
        If an action is found, then it is validated against ImpossibleAt/ImpossibleIf statements
        :param model: The model to be validated
        :param time: The time at which we check/validate the model
        :return: A tuple of 4 elements, first is a bool that says whether or not model is valid
        second is the action that is affecting the model passed into the method, and the third either None (if no statements associated with action were found)
        or a Effect statement that contains the action to be executed along with associated agent
        that is correlated with the action. 4th returns error string
        """
        current_statements = {'releases': None, 'causes': None}
        statement_to_be_executed = None
        current_action = None
        expr = None
        expr_values = None
        action_src = None
        err_str = "No error"
        action_times = self.actions_at_time_t.keys()
        triggered_action_times = None if model.triggered_actions is None else model.triggered_actions.keys()
        t = time - 1
        action_from_acs_executed_now = t in action_times
        triggered_action_executed_now = False if triggered_action_times is None else t in triggered_action_times

        if action_from_acs_executed_now and triggered_action_executed_now:
            err_str = "Model is invalid because 2 actions are executed at time: {}\n{} {}".format(t,
                                                                                                  self.actions_at_time_t[
                                                                                                      t],
                                                                                                  model.triggered_actions[
                                                                                                      t])
            return False, None, None, err_str
        elif action_from_acs_executed_now:
            action_src = self.actions_at_time_t
        elif triggered_action_executed_now:
            action_src = model.triggered_actions
        else:
            # If no action is affecting us now, assume model is valid
            return True, None, None, err_str

        action = action_src[t]
        for statement in self.joined_statements[action.name]:
            if statement.action == action.name and action.begin_time + statement.duration == time and statement.agent == action.agent:
                evaluation = None
                current_action = action
                if statement.duration <= action.duration:  # Use only statements which duration can be filled in the action occurence
                    if expr is None or expr_values is None:
                        # We found an ActionOccurrence, let's get the symbol values in the model at the time it occurred
                        # So we can evaluate action preconditions against them
                        expr, expr_values = model.get_symbol_values(current_action.begin_time)
                    if isinstance(statement.condition, bool):
                        # By default EffectStatements have a bool value for condition, this if statement handles that
                        evaluation = statement.condition
                    else:
                        # Our statement in the domain description has a precondition, validate it against our model
                        evaluation = self.evaluate(expr, expr_values, statement.condition.formula)
                    if evaluation and isinstance(statement, Causes):
                        # Our statement precondition holds, so we add it to the returned statements
                        if current_statements['causes'] is None:
                            current_statements['causes'] = statement
                        else:
                            # We already have a Causes statement, so join its effect with the existing one
                            # This case handles the following scenario:
                            # Load causes ~hidden by A
                            # Load causes loaded by A
                            # Both statements are joined into 1 larger one: Load causes ~hidden & loaded by A
                            current_statements['causes'] = self.join_statement_by_and(current_statements['causes'],
                                                                                      statement, is_causes=True)
                    elif evaluation and isinstance(statement, Releases):
                        # Our statement precondition holds, so we add it to the returned statements
                        if current_statements['releases'] is None:
                            current_statements['releases'] = self.create_tautology_from_statements(statement, statement)
                        else:
                            current_statements['releases'] = self.create_tautology_from_statements(
                                current_statements['releases'], statement)

        if current_action is None:
            # If no action is affecting us now, assume model is valid
            # Action is executed with empty effect because no agent can execute it
            return True, None, None, err_str

        if (current_statements['causes'] is not None) and (current_statements['releases'] is not None):
            statement_to_be_executed = self.join_statement_by_and(current_statements['causes'],
                                                                  current_statements['releases'], is_causes=True)
        elif current_statements['causes'] is not None:
            statement_to_be_executed = current_statements['causes']
        elif current_statements['releases'] is not None:
            statement_to_be_executed = current_statements['releases']

        # TODO not needed probably slight optimization
        # if model.triggered_actions is not None:
        #     model.triggered_actions = None

        """
        Incorrect behavior
        if current_statements['causes'] is not None and current_statements['releases'] is not None:
            # Since at this time the model is affected by releases AND causes statements...
            # we must join the causes/releases effect by and into 1 releases effect.
            # This is because the causes statements will ALWAYS occur, and the releases effect MAY occur
            # Example: imagine we have the following 2 statements in our DD:
            # Load causes loaded
            # Load releases ~hidden
            # What will happen? The fluent "loaded" will ALWAYS hold in the new model because it is CAUSED
            # The fluent "~hidden" may or may not hold because it is RELEASED. So we create a new releases statement:
            # "Load releases loaded & ~hidden", now our engine will fork models where "loaded & ~hidden"
            # may or may not hold, but "loaded" will always hold because we have a causes statement for it
            current_statements['releases'] = self.join_statement_by_and(current_statements['releases'],
                                                                        current_statements['causes'], False)
        """

        # Check ImpossibleBy/ImpossibleIf
        if self.action_impossible_if(current_action, expr, expr_values):
            err_str = "Impossible if holds at time {} Action: {} Fluents: {} Values: {}".format(t, current_action.name, expr, expr_values)
            return False, None, None, err_str
        if self.action_impossible_by(action):
            err_str = "Impossible by holds at time {} Action: {} Agent: {}".format(t, current_action.name, current_action.agent)
            return False, None, None, err_str

        return True, current_action, statement_to_be_executed, err_str

    def remove_bad_observations(self, models: List[Model], time: int):
        """
        This method is executed after forking new models. 
        It may happen that a newly forked model violates an observation that we had at a given time,
        if so we must remove it.
        :param models: The list of models that will be checked for invalid state of fluents,
        the models it stores may be removed. 
        :param time: The time at which the observations will be checked
        :return: None
        """
        for i in range(len(models) - 1, -1, -1):
            is_valid = True
            expr, expr_values = models[i].get_symbol_values(time)
            if time in self.observations_at_time_t:
                for obs in self.observations_at_time_t[time]:
                    evaluation = self.evaluate(expr, expr_values, obs.condition.formula)
                    # print('(Observations) Expression:', expr, 'given values:', expr_values, 'in the formula:',
                    #       obs.condition.formula, 'was evaluated to:',
                    #       evaluation, 'at time:', time)
                    # Invalid model, so we don't even try to find an action for this time
                    if evaluation != True:
                        is_valid = False
            if not is_valid:
                models.remove((models[i]))

    @staticmethod
    def evaluate(symbols: List[Symbol], symbol_values: List[bool], formula: boolalg.Boolean) -> bool:
        """
        Methods evaluates a logical (boolean formula) given the True/False value of each symbol
        :param symbols: A list of sympy symbols to be checked in the formula.
        Warning: order corresponds to order of "symbol_values"! The value of symbols[2] is symbol_values[2]
        and len(symbols) == len(symbol_values)
        :param symbol_values: The True/False values associated with the list of symbols
        :param formula: The formula that will be evaluated given the symbols with their values
        :return: True if formula is satisfied, False otherwise
        """
        # Using the lambdify() method, we can evaluate a boolean formula given state of boolean variables
        # There is no "eval()" method in sympy for solving boolean formulas
        # https://stackoverflow.com/questions/42045906/typeerror-return-arrays-must-be-of-arraytype-using-lambdify-of-sympy-in-python
        f = lambdify(symbols, formula, modules={'And': any, 'Or': all})
        combinations = InconsistencyChecker.get_all_combinations(symbol_values)
        eval = f(*combinations[0])
        for i in range(1, len(combinations)):
            if f(*combinations[i]) != eval:
                return None
        return eval

    @staticmethod
    def evaluate_trigger(symbols_pre: List[Symbol], symbol_values_pre: List[bool], symbols: List[Symbol], symbol_values: List[bool], formula: boolalg.Boolean) -> bool:

        t = 0
        f = lambdify(symbols_pre, formula, modules={'And': any, 'Or': all})
        combinations = InconsistencyChecker.get_all_combinations(symbol_values_pre)
        eval = f(*combinations[0])
        for i in range(1, len(combinations)):
            if f(*combinations[i]) != eval:
                return None;
        if not eval:
            f = lambdify(symbols, formula, modules={'And': any, 'Or': all})
            combinations = InconsistencyChecker.get_all_combinations(symbol_values)
            eval = f(*combinations[0])
            for i in range(1, len(combinations)):
                if f(*combinations[i]) != eval:
                    return None
            return eval
        else:
            return False

    @staticmethod
    def get_all_combinations(symbol_values: List[bool]) -> List[List[bool]]:
        combinations = []
        combinations.append(symbol_values)
        for i in range(len(symbol_values)):
            if symbol_values[i] is None:
                new_comb = []
                for comb in combinations:
                    copy = list(comb)
                    copy2 = list(comb)
                    copy[i] = False
                    new_comb.append(copy)
                    copy2[i] = True
                    new_comb.append(copy2)
                combinations = new_comb
        return combinations

    def join_statement_by_and(self, statement1: Statement, statement2: Statement, is_causes: bool) -> Statement:
        if is_causes:
            return Causes(action=statement1.action,
                          effect=Condition(And(statement1.effect.formula, statement2.effect.formula)),
                          duration=statement1.duration, agent=statement1.agent)
        else:
            return Releases(action=statement1.action,
                            effect=Condition(And(statement1.effect.formula, statement2.effect.formula)),
                            duration=statement1.duration, agent=statement1.agent)

    """
    Returns a Releases statement that will have a formula that holds for all input (tautology)
    So if we have the formula "loaded" it will create "loaded or ~loaded" 
    This statement will hold if "loaded" is true or false, we need this for the engine
    """

    def create_tautology_from_statements(self, statement1: Statement, statement2: Statement) -> Statement:
        return Releases(action=statement1.action,
                        effect=Condition(Or(statement1.effect.formula, Not(statement2.effect.formula))),
                        duration=statement1.duration, agent=statement1.agent)

    def action_impossible_at(self, action: ActionOccurrence) -> bool:
        """
        :param action: Action to be validated against ImpossibleAt statements
        :return: True if action cannot be executed at the given time, False otherwise
        """
        if action.begin_time in self.action_time_constraints_at_time_t:
            if action.name in self.action_time_constraints_at_time_t[action.begin_time]:
                # print('action:', action, 'violates impossible_at at time:', action.begin_time)
                return True
        return False

    def action_impossible_if(self, action: ActionOccurrence, expr: List[Symbol], expr_values: List[bool]) -> bool:
        """
        Method takes and action, and sees if the some ImpossibleIf holds for it
        :param action: The action to be checked
        :param expr: The expression that holds in the model at the time of checking the ImpossibleIf (state of fluents)
        For example expr can be [loaded, hidden] and expr_values [True, False] that corresponds to the statement loaded & ~hidden
        :param expr_values: The corresponding True/False values of the symbols in expr
        :return: True if action execution is impossible due to ImpossibleIf holding, False otherwise
        """

        for impossible_if in self.action_formula_constraints:
            if action.name == impossible_if.action:
                evaluation = self.evaluate(expr, expr_values, impossible_if.condition.formula)
                # print('(ImpossibleIf) Expression:', expr, 'given values:', expr_values, 'in the formula:',
                #       impossible_if.condition.formula,
                #       'was evaluated to:',
                #       evaluation, 'for action:', action.name, 'at time:', action.begin_time)
                # Invalid model, so we don't even try to find an action for this time
                if evaluation:
                    # print('action:', action, 'violates impossible_if:', impossible_if, 'at time:', action.begin_time,
                    #       'expr:',
                    #       expr, 'expr_values:', expr_values)
                    return True
        return False

    def action_impossible_by(self, action: ActionOccurrence) -> bool:
        for impossible_by in self.impossible_by_statements:
            if impossible_by.action == action.name and action.agent == impossible_by.agent:
                return True
        return False
