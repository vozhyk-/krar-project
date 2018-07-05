from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from structs.fluent import Fluent
from structs.action_occurrence import ActionOccurrence
from structs.observation import Observation
from typing import List
import parsing.domain_description, parsing.scenario
from sympy.logic.inference import satisfiable
from numpy import ndarray


class Model:
    def __init__(self, scenario: Scenario):
        # self.domain_description = domain_description
        self.scenario = scenario
        self.fluents = self.parse_initial_fluents()
        # self.consistent = False  # still to be checked later on
        last_action = self.scenario.action_occurrences[-1]
        self.last_time_point = last_action.begin_time + last_action.duration + 1
        self.fluent_history = self.initialize_history()

    def initialize_history(self) -> ndarray:
        fluent_history = ndarray(shape=(self.last_time_point, len(self.fluents)), dtype=Fluent)
        for observation in self.scenario.observations:
            for key, value in satisfiable(observation.condition.formula).items():
                fluent = Fluent(key.name, value)
                begin_time = observation.begin_time
                for i in range(0, len(fluent_history[begin_time])):
                    if fluent_history[begin_time][i] is None:
                        fluent_history[begin_time][i] = fluent
                        break
                    else:
                        continue
        return fluent_history

    def history_function(self, fluent: Fluent, time_point: int):
        time_point_row = self.fluent_history[time_point]
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

    def parse_initial_fluents(self):
        fluents = []
        for observation in self.scenario.observations:
            if observation.begin_time == 0:
                for key, value in satisfiable(observation.condition.formula).items():
                    fluents.append(Fluent(key.name, value))

        return fluents

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
