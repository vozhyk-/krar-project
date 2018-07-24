from engine.inconsistency_checker import InconsistencyChecker
from engine.model import Model
from sympy.logic import boolalg
from structs.statements import Causes, Releases, Statement, EffectStatement
from structs.action_occurrence import ActionOccurrence
from typing import List, Dict, Optional
from copy import deepcopy
from sympy.logic.inference import satisfiable


class Engine:
    def __init__(self, checker: InconsistencyChecker):
        """
        :param checker: An instance of the InconsistencyChecker that will validate models,
        and perform helper tasks such as removing duplicate models
        """
        self.checker = checker
        self.models = []
        self.run()
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

    def run(self):
        """
        The most important method of the Engine class. It runs the algorithm described above
        and it creates a list of all valid models and stores them in the "self.models" class member
        """
        # Create initial model which corresponds to the initial state
        initial_model = Model(self.checker.valid_scenario)
        # We may have more than 1 initial model
        self.models += self.fork_model(initial_model, self.checker.sorted_observations[0].condition.formula, 0, True)
        self.models = self.checker.remove_duplicate_models(self.models)
        i = 0
        for m in self.models:
            print('Initial model:', i, '\n', m)
            i += 1

        total_time = initial_model.fluent_history.shape[0]
        for t in range(total_time):
            # Check OBS/ACS at time t and fork model accordingly
            # Only one action can be executed at a time
            print('At time', t, 'we have', len(self.models), 'models')
            new_models = []
            for i in range(len(self.models) - 1, -1, -1):
                is_model_valid, action, statements = self.checker.validate_model(self.models[i], t)
                if not is_model_valid:
                    print('Model:\n', self.models[i], 'IS NOT VALID at time:', t)
                    self.models.remove(self.models[i])
                elif action is not None:
                    new_models += self.execute_action(self.models[i], action, statements)
            self.models += new_models
            # After forking the new models,
            # we can now check if some of our observations invalidate the newly forked models
            self.checker.remove_bad_observations(self.models, t)
            # Remove duplicates
            self.models = self.checker.remove_duplicate_models(self.models)

    def fork_model(self, model: Model, formula: boolalg.Boolean, time: int, is_releases_statement: bool = False) -> \
            List[Model]:
        """
        Checks all solutions to formula  for a given "causes" or "releases" statement and 
        uses satisfiable() and creates a model for each solution holding at time t
        :param model: The model to be forked, it could be removed from the list of models if
        :param formula: The sympy boolean formula that must hold at this time
        :param time: The time at which the action effect given by "formula" must hold in the model
        :param is_releases_statement: If true, then we keep the model that we want to fork. 
        If false, it means we want to fork based on a CAUSES statement,
        so we remove the model that was passed in because we only want to have models where formula MUST HOLD
        :return: The list of new models obtained from solutions of the parameter "formula"
        """
        new_models = []
        solutions = satisfiable(formula, all_models=True)

        for s in solutions:
            new_model = deepcopy(model)
            new_model.update_fluent_history(s, time)
            new_models.append(new_model)

        if not is_releases_statement and model in self.models:
            self.models.remove(model)

        return new_models

    def execute_action(self, model: Model, action: ActionOccurrence, statements: Dict[str, EffectStatement]) -> List[Model]:
        """
        We take an action occurrence (from a scenario) and the EffectStatement that is correlated with it,
        then we attempt to fork models based on the statement's boolean formula
        :param model: The model in which we wish to execute the given action
        :param action: The action occurrence which is affecting the model at the current time
        :param statements: A dict that contains 2 keys 'releases' and 'causes'
        storing the Releases and Causes statement affecting the model at this time
        :return: The list of models that has been forked
        """
        new_models = []
        if statements['releases'] is not None:
            new_models += self.fork_model(model, statements['releases'].effect.formula, action.begin_time + statements['releases'].duration, True)
        if statements['causes'] is not None:
            new_models += self.fork_model(model, statements['causes'].effect.formula, action.begin_time + statements['causes'].duration, False)

        return new_models
