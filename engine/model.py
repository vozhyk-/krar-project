
from structs.scenario import Scenario
from structs.fluent import Fluent
from structs.action_occurrence import ActionOccurrence
from typing import List, Tuple
from sympy.logic.inference import satisfiable
from numpy import ndarray
from copy import deepcopy
import sympy.parsing.sympy_parser as sympy_parser
import sympy
from sympy.core.symbol import Symbol
from sympy.logic import boolalg


class Model:
    def __init__(self, scenario: Scenario, fluents: List[Symbol], initial_condition: boolalg.Boolean):
        # self.domain_description = domain_description
        # self.scenario = scenario
        self.fluents = fluents
        # self.consistent = False  # still to be checked later on
        acs = sorted(scenario.action_occurrences, key=lambda action: action.begin_time)
        last_action = acs[-1]
        self.last_time_point = last_action.begin_time + last_action.duration + 1
        self.fluent_history = self.initialize_history(initial_condition)
        self.action_history = dict()
        self.triggered_actions = None  # time: int -> statement

    def initialize_history(self, initial_condition: boolalg.Boolean) -> ndarray:
        fluent_history = ndarray(shape=(self.last_time_point, len(self.fluents)), dtype=Fluent)
        '''
        for observation in sorted_observations:
            for key, value in satisfiable(observation.condition.formula).items():
                fluent = Fluent(key.name, value)
                begin_time = observation.begin_time
                for i in range(len(fluent_history[begin_time])):
                    if fluent_history[begin_time][i] is None:
                        fluent_history[begin_time][i] = fluent
                        break
                    else:
                        continue
        '''
        for key, value in satisfiable(initial_condition).items():
            fluent = Fluent(key.name, value)
            begin_time = 0
            for i in range(len(fluent_history[begin_time])):
                if fluent_history[begin_time][i] is None:
                    fluent_history[begin_time][i] = fluent
                    break
                else:
                    continue
        # Assume inertia law
        for i in range(fluent_history.shape[0] - 1):
            for j in range(fluent_history.shape[1]):
                if fluent_history[i][j] is not None and fluent_history[i + 1][j] is None:
                    fluent_history[i + 1][j] = deepcopy(fluent_history[i][j])

        return fluent_history

    def history_function(self, fluent: Fluent, time_point: int):
        time_point_row = self.fluent_history[self.clamp_time(time_point)]
        if time_point_row.__contains__(fluent):
            return fluent.value
        else:
            return None

    def occlusion_function(self, action: ActionOccurrence):
        fluents_under_influence = []
        start_time = action.begin_time
        end_time = start_time + action.duration + 1
        for i in range(start_time, end_time):
            for fluent in self.fluent_history[i]:
                if fluent is not None:
                    fluents_under_influence.append(fluent)

        return fluents_under_influence

    def update_fluent_history(self, solution: dict, time: int, duration: int):
        for key, value in solution.items():
            for j in range(self.fluent_history.shape[1]):
                if str(key) == self.fluent_history[time][j].name:
                    self.fluent_history[time][j].value = value
                    if ((duration > 1)
                    and (time - duration >= 0)
                    and (self.fluent_history[time][j].value != self.fluent_history[time - duration][j].value)):
                        for t in range(time - duration + 1, time):
                            self.fluent_history[t][j].value = None

        # Assume inertia law
        for i in range(time + 1, self.fluent_history.shape[0]):
            for j in range(self.fluent_history.shape[1]):
                self.fluent_history[i][j] = deepcopy(self.fluent_history[i - 1][j])

    def clamp_time(self, time: int):
        return min(time, self.last_time_point - 1)

    def get_symbol_values(self, time: int) -> Tuple[List[sympy.Symbol], List[bool]]:
        """
        Method converts a row of "Fluent" objects to a tuple of 2 lists 
        The value of the sympy symbol can be true or false at a given time,
        this helper method helps us evaluate fluents against a formula
        :param time: The time at which the row of sympy symbols is taken
        :return: A tuple of 2 lists, one list stores the sympy symbols
        while the second stores the boolean values associated with them
        """
        current_fluents = self.fluent_history[self.clamp_time(time)]
        fluent_symbol_dict = dict()  # SympySymbol -> bool
        # Convert state of fluents to sympy dict
        # https://stackoverflow.com/questions/42024034/evaluate-sympy-boolean-expression-in-python
        for fluent in current_fluents:
            fluent_symbol_dict[sympy_parser.parse_expr(fluent.name)] = fluent.value
        expr = list(fluent_symbol_dict.keys())
        expr_values = list(fluent_symbol_dict.values())
        return expr, expr_values

    def add_to_action_history(self, time: int, action: ActionOccurrence):
        self.action_history[time] = action

    def __str__(self):
        string = ''
        for i in range(self.fluent_history.shape[0]):
            string += 'Timepoint ' + str(i) + ': '
            for j in range(self.fluent_history.shape[1]):
                if self.fluent_history[i][j] is not None:
                    string += self.fluent_history[i][j].name + ' ' + str(self.fluent_history[i][j].value)
                else:
                    string += 'None'
                if j != self.fluent_history.shape[1] - 1:
                    string += ', '
            string += '\n'
        return string

    def __eq__(self, other):
        if isinstance(other, Model):
            return (self.fluent_history == other.fluent_history).all()
        return False
