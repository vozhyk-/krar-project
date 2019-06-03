from engine.inconsistency_checker import InconsistencyChecker
from engine.model import Model
from sympy.logic import boolalg
from sympy.core.symbol import Symbol
from sympy.logic.boolalg import BooleanFalse, Or, Not
from structs.statements import Causes, Releases, Statement, EffectStatement, Triggers, ImpossibleIf
from structs.action_occurrence import ActionOccurrence
from typing import List, Dict, Optional
from copy import deepcopy
from sympy.logic.inference import satisfiable
from engine.preprocessor import Preprocessor
from structs.scenario import Scenario
from structs.domain_description import DomainDescription
import parsing.scenario
import parsing.domain_description
import parsing.query


class Engine:
    def __init__(self):

        self.checker = None
        self.models = []
        # self.run()

    '''
    //////////////////////////////
    //////////ALGORITHM///////////
    //////////////////////////////
    
    1. Define initial models based on initial state (using satisfiable()), and add them to list of models
    2. Loop through the whole time of the scenario
        a. Find observations and the 1 action that occurs at time point t
        b. Loop though list of current models
            b2. Find the action that occurs at some time k such that k+d=t (The action that is affecting the model now)
                i. If action violates domain description ImpossibleAt or ImpossibleIf (at time k) statements:
                    *. Model won't be forked, go to step b
                ii. If action precondition at time k does not hold:
                    *. Model won't be forked, go to step b
                iv. If action CAN be executed at time k and it is a CAUSES statement:
                    *. Execute the CAUSES action, so make a deepcopy of the model for all solutions
                     to the boolean formula of the action effect
                     **. Remove the model that occurred at time k because it is no loner valid
                v. If action CAN be executed and it is a RELEASES statement:
                    *. Execute the RELEASES action, so make a deepcopy of the model for all solutions
                     to the boolean formula of the action effect while keeping the original model   
            b3. Loop through list of observations at time t 
            (Note that this occurs AFTER executing the action affecting the current model and modifying the fluents)
                i. If current state of fluents in this model at time t do not satisfy formula in observation
                    *. Remove this model from the list of models and go to step b (check next model)
    '''

    def run(self, scenario: Scenario, domain_desc: DomainDescription):
        """
        The most important method of the Engine class. It runs the algorithm described above
        and it creates a list of all valid models and stores them in the "self.models" class member
        :param scenario: Domain description that will be used for running the model
        :param domain_desc: 
        :return: True if method was successful (data is consistent) False otherwise
        """
        prec = Preprocessor()
        unique_domain_desc, unique_scenario = prec.remove_duplicates(domain_desc, scenario)
        # After pre-processing the domain desc and scenario, pass it to the inconsistency_checker
        self.checker = InconsistencyChecker(unique_domain_desc, unique_scenario)
        if not self.checker.is_consistent:
            print('in Model.run(): InconsistencyChecker claims scenario and/or domain description is invalid')
            return False
        # Create initial model which corresponds to the initial state
        fluents = self.get_all_fluents(self.checker.domain_desc)
        initial_condition = self.create_initial_condition(self.checker.valid_scenario, fluents)
        initial_model = Model(self.checker.valid_scenario, fluents, initial_condition)
        # We may have more than 1 initial model
        self.models += self.fork_model(initial_model, initial_condition, 0, 0)
        self.models = self.checker.remove_duplicate_models(self.models)
        # i = 0
        # for m in self.models:
        #     print('Initial model:', i, '\n', m)
        #     i += 1

        total_time = initial_model.fluent_history.shape[0]
        for t in range(total_time):
            # Check OBS/ACS at time t and fork model accordingly
            # Only one action can be executed at a time
            new_models = []
            for i in range(len(self.models) - 1, -1, -1):
                is_model_valid, action, statements, err_str = self.checker.validate_model(self.models[i], t)
                if not is_model_valid:
                    print('Model:\n', self.models[i], 'IS NOT VALID at time:', t - 1)
                    print("Reason:", err_str)
                    self.models.remove(self.models[i])
                elif action is not None:
                    self.models[i].add_to_action_history(action.begin_time, action)
                    new_models += self.execute_action(self.models[i], action, statements)
            self.models += new_models
            # After forking the new models,
            # we can now check if some of our observations invalidate the newly forked models
            self.checker.remove_bad_observations(self.models, t)
            # Remove duplicates
            self.models = self.checker.remove_duplicate_models(self.models)
            self.handle_trigger_statements(time=t)
            print('At time', t, 'we have', len(self.models), 'models')

        return True

    def fork_model(self, model: Model, formula: boolalg.Boolean, time: int, duration: int) -> \
            List[Model]:
        """
        Checks all solutions to formula  for a given "causes" or "releases" statement and 
        uses satisfiable() and creates a model for each solution holding at time t
        :param model: The model to be forked, it could be removed from the list of models if
        :param formula: The sympy boolean formula that must hold at this time
        :param time: The time at which the action effect given by "formula" must hold in the model
        :param duration: The duration of action is used for occlusion regions
        :param is_releases_statement: If true, then we keep the model that we want to fork. 
        If false, it means we want to fork based on a CAUSES statement,
        so we remove the model that was passed in because we only want to have models where formula MUST HOLD
        :return: The list of new models obtained from solutions of the parameter "formula"
        """
        new_models = []
        solutions = satisfiable(formula, all_models=True)

        for s in solutions:
            if s is not False:
                new_model = deepcopy(model)
                new_model.update_fluent_history(s, time, duration)
                new_models.append(new_model)

        if model in self.models:
            self.models.remove(model)

        return new_models

    def execute_action(self, model: Model, action: ActionOccurrence,
                       statement_to_be_executed: Optional[EffectStatement]) -> List[Model]:
        """
        We take an action occurrence (from a scenario) and the EffectStatement that is correlated with it,
        then we attempt to fork models based on the statement's boolean formula
        :param model: The model in which we wish to execute the given action
        :param action: The action occurrence which is affecting the model at the current time
        :param statement_to_be_executed: Optional effect statement of action that will be executed
        :return: The list of models that has been forked
        """
        new_models = []
        if statement_to_be_executed is not None:
            new_models += self.fork_model(model, statement_to_be_executed.effect.formula,
                                          action.begin_time + statement_to_be_executed.duration,
                                          statement_to_be_executed.duration)

        return new_models

    def handle_trigger_statements(self, time: int):
        for model in self.models:
            expr, expr_values = model.get_symbol_values(time)
            # expr_pre, expr_values_pre = model.get_symbol_values(time-1)
            for statement in self.checker.domain_desc.statements:
                if isinstance(statement, Triggers):
                    # evaluation = self.checker.evaluate_trigger(expr_pre, expr_values_pre, expr, expr_values, statement.condition.formula)
                    evaluation = self.checker.evaluate(expr, expr_values, statement.condition.formula)
                    if evaluation:
                        # model.triggered_actions = {time: ActionOccurrence(statement.action, time, statement.agent, 1)}
                        model.triggered_actions = {time: ActionOccurrence(statement.action, time, 'nobody', 1)}

    def get_all_fluents(self, domain_description: DomainDescription):
        fluents = []
        for statement in domain_description.statements:
            if isinstance(statement, EffectStatement):
                fluents = list(set(fluents) | set(statement.effect.formula.atoms()))
                if statement.condition is not True:
                    fluents = list(set(fluents) | set(statement.condition.formula.atoms()))
            if isinstance(statement, Triggers) or isinstance(statement, ImpossibleIf):
                if statement.condition.formula is not True:
                    fluents = list(set(fluents) | set(statement.condition.formula.atoms()))
        return fluents

    def create_initial_condition(self, scenario: Scenario, fluents: List[Symbol]):
        initial_statement = BooleanFalse
        if len(scenario.observations) != 0 and scenario.observations[0].begin_time == 0:
            initial_statement = scenario.observations[0].condition.formula
            not_used_fluents = list(set(fluents) - set(scenario.observations[0].condition.formula.atoms()))
            for fluent in not_used_fluents:
                initial_statement = Or(initial_statement, Or(fluent, Not(fluent)))
        else:
            for fluent in fluents:
                if initial_statement is BooleanFalse:
                    initial_statement = Or(fluent, Not(fluent))
                else:
                    initial_statement = Or(initial_statement, Or(fluent, Not(fluent)))
        return initial_statement
