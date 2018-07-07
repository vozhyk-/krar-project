from engine.inconsistency_checker import InconsistencyChecker
from engine.model import Model
from sympy.logic import boolalg
from structs.statements import ImpossibleAt, ImpossibleIf, Causes, Releases
from structs.action_occurrence import ActionOccurrence
from typing import List
from copy import deepcopy
from sympy.logic.inference import satisfiable


class Engine:
    def __init__(self, checker: InconsistencyChecker):
        self.checker = checker
        self.models = []
        # Create initial model which corresponds to the initial state
        self.run()

    # We will check observations/action occurrences in the valid scenario and fork models according to
    # https://github.com/vozhyk-/krar-project/issues/3
    '''
    //////////////////////////////
    //////////ALGORITHM///////////
    //////////////////////////////
    
    1. Define initial models based on initial state (using satisfiable()), and add them to list of models
    2. Loop through the whole time of the scenario
        a. Find observations and the 1 action that occurs at time point t
        b. Loop though list of current models
            b2. Loop through list of observations at time t
                i. If current state of fluents in this model at time t do not satisfy formula in observation
                    *. Remove this model from the list of models and go to step b (check next model)
            b3. Check action at time t (only 1 action executed at a time)
                i. If action violates domain description ImpossibleAt and ImpossibleIf statements:
                    *. Model won't be forked, go to step b
                ii. If action precondition is not satisfied:
                    *. Model won't be forked, go to step b
                iv. If action CAN be executed and it is a CAUSES statement:
                    *. Execute effect of action in current model (change fluents at t+d) 
                    and fork models for all other solutions to formula
                v. If action CAN be executed and it is a RELEASES statement:
                    *. Leave existing model unchanged,
                     however we fork (create new copies of) models where formula holds at t+d          
                NOTE: If the formulas holding in steps "iv" and "v" have more than one solution
                (they contain logical or for example or an implication), then we
                check all solutions using satisfiable() and fork the model where solution holds at time t+d
                  
    '''

    def run(self):
        initial_model = Model(self.checker.valid_scenario)
        print('initial_model:\n', initial_model)
        self.models.append(initial_model)
        # TODO Can we have more than 1 initial model? For example OBS= loaded | hidden? if so uncomment below
        '''
        for model in self.fork_model(initial_model, self.checker.sorted_observations[0].condition.formula, 0, True):
            self.models.append(model)
        self.models = self.checker.remove_duplicate_models(self.models)
        print('self.models:')
        for m in self.models:
            print(m)
        '''
        total_time = initial_model.fluent_history.shape[0]
        for t in range(total_time):
            # Check OBS/ACS at time t and fork model accordingly
            # Only one action can be executed at a time
            new_models = []
            for i in range(len(self.models) - 1, -1, -1):
                is_model_valid, action = self.checker.validate_model(self.models[i], t)
                if not is_model_valid:
                    print('Model:\n', self.models[i], '\n IS NOT VALID')
                    self.models.remove(self.models[i])
                elif action is not None:
                    for new_model in self.execute_action(self.models[i], t, action):
                        new_models.append(new_model)
            self.models += new_models
            self.models = self.checker.remove_duplicate_models(self.models)

    # Checks all solutions to formula uses satisfiable() and creates a model for each solution holding at time t
    # If is_releases_statement, it means we must also add the model passed to the method
    # Because a releases statement leads to a state where the condition doesn't necessarily have to hold
    # However adding the model pass to the method to the list could lead to duplicates
    def fork_model(self, model: Model, formula: boolalg.Boolean, time: int, is_releases_statement: bool = False) -> List[Model]:
        new_models = []
        solutions = satisfiable(formula, all_models=True)
        if is_releases_statement:
            new_models.append(model)
        for s in solutions:
            new_model = deepcopy(model)
            new_model.update_fluent_history(s, time)
            new_models.append(new_model)

        # Remove duplicates
        self.models = self.checker.remove_duplicate_models(self.models)
        return new_models

    def execute_action(self, model: Model, time: int, action: ActionOccurrence) -> List[Model]:
        new_models = []
        for statement in self.checker.domain_desc.statements:
            if isinstance(statement, Causes) and statement.action == action.name:
                for new_model in self.fork_model(model, statement.effect.formula, time, False):
                    new_models.append(new_model)
            elif isinstance(statement, Releases) and statement.action == action.name:
                for new_model in self.fork_model(model, statement.effect.formula, time, True):
                    new_models.append(new_model)
        return new_models