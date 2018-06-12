from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from structs.fluent import Fluent
from structs.action_occurrence import ActionOccurrence
import parsing.domain_description, parsing.scenario
from sympy.logic.inference import satisfiable
import numpy


class Model:
    def __init__(self, domain_description: DomainDescription, scenario: Scenario):
        self.domain_description = domain_description
        self.scenario = scenario
        self.fluents = self.parse_initial_fluents()
        self.consistent = False
        last_action = scenario.action_occurrences[-1]
        self.last_time_point = last_action.begin_time + last_action.duration + 1
        self.fluent_history = numpy.zeros(shape = (len(self.fluents), self.last_time_point))

    def history_function(self, fluent: Fluent, time_point: int):
        row = self.get_fluent_row(fluent)
        if row != -1:
            if time_point < self.last_time_point:
                return self.fluent_history[row, time_point]
            else:
                return self.fluent_history[row, -1]
        return None

    def get_fluent_row(self, fluent: Fluent):
        row = -1
        for i in range(len(self.fluents)):
            if self.fluents[i].name == fluent.name:
                row = i
                break
        return row

    def occlusion_function(self, action: ActionOccurrence, time_point: int):
        pass

    def parse_initial_fluents(self):
        fluents = []
        for observation in self.scenario.observations:
            if observation.begin_time == 0:
                for key, value in satisfiable(observation.condition.formula).items():
                    fluents.append(Fluent(key.name, value))

        return fluents


md = Model(domain_description=parsing.domain_description.parse_file("../example/lib.adl3"),
           scenario=parsing.scenario.parse_file("../example/scenario.txt"))
