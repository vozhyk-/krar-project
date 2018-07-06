from engine.inconsistency_checker import InconsistencyChecker
from engine.model import Model
from sympy.logic import boolalg
from structs.statements import ImpossibleAt, ImpossibleIf
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
        a. Find observations and actions occurring at specific time point t
        b. Loop though list of current models
            b2. Loop through list of actions occurring at time t
                i. If action violates domain description ImpossibleAt and ImpossibleIf statements:
                    *. Go to step "b2" and check next action (skip the steps below)
                ii. If action precondition is not satisfied:
                    *. Go to step "b2" and check next action (skip the steps below)
                iv. If action CAN be executed and it is a CAUSES statement:
                    *. Execute effect of action in current model (change fluents at t+d) 
                    and fork models for all other solutions to formula
                v. If action CAN be executed and it is a RELEASES statement:
                    *. Leave existing model unchanged,
                     however we fork (create new copies of) models where formula holds at t+d          
                NOTE: If the formulas holding in steps "iv" and "v" have more than one solution
                (they contain logical or for example or an implication), then we
                check all solutions using satisfiable() and fork the model where solution holds at time t+d
            b3. Loop through list of observations at time t
                i. If current state of fluents at time t do not satisfy formula in observation
                    *. Remove this model from the list of models       
    '''

    def run(self):
        initial_model = Model(self.checker.valid_scenario)
        # print('initial_model:\n', initial_model)
        self.fork_model(initial_model, self.checker.sorted_observations[0].condition.formula, 0)
        print('self.models:')
        for m in self.models:
            print(m)
        total_time = initial_model.fluent_history.shape[0]
        # Checked when looping through models, some models may/may not be removed
        action_formula_constraints = [fc for fc in self.checker.domain_desc.statements if
                                      isinstance(fc,
                                                 ImpossibleIf)]
        # TODO implement below according to algorithm described above
        for t in range(total_time):
            # Check OBS/ACS at time t and fork model accordingly
            actions_at_time_t = [ac for ac in self.checker.sorted_actions if ac.begin_time == t]
            observations_at_time_t = [ob for ob in self.checker.sorted_observations if
                                      ob.begin_time == t]  # This applies to all models
            action_time_constraints = [ac for ac in self.checker.domain_desc.statements if
                                       isinstance(ac, ImpossibleAt) and ac.time == t]  # This applies to all models
            for model in self.models:
                current_state_of_fluents = model.fluent_history[t]

    # Checks all solutions to formula uses satisfiable() and creates a model for each solution holding at time t
    # If is_releases_statement, it means we must also add the model passed to the method
    # Because a releases statement leads to a state where the condition doesn't necessarily have to hold
    # However adding the model pass to the method to the list could lead to duplicates
    # TODO Remove duplicate models at the end of this method (implement inconsistency_checker.py)
    def fork_model(self, model: Model, formula: boolalg.Boolean, time: int, is_releases_statement: bool = False):
        solutions = satisfiable(formula, all_models=True)
        if is_releases_statement:
            self.models.append(model)
        for s in solutions:
            new_model = deepcopy(model)
            new_model.update_fluent_history(s, time)
            self.models.append(new_model)
