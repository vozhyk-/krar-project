from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from structs.fluent import Fluent
from structs.action_occurrence import ActionOccurrence
import parsing.domain_description, parsing.scenario
from sympy.logic.inference import satisfiable
from numpy import ndarray


class Model:
    def __init__(self, domain_description: DomainDescription, scenario: Scenario):
        self.domain_description = domain_description
        self.scenario = scenario
        self.fluents = self.parse_initial_fluents()
        self.consistent = False  # still to be checked later on
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

    def history_function(self, fluent: Fluent, time_point: int) -> bool:
        time_point_row = self.fluent_history[time_point]
        return time_point_row.__contains__(fluent)

    def occlusion_function(self, action: ActionOccurrence, time_point: int = None):
        fluents_under_influence = []
        start_time = time_point if time_point >= 0 else action.begin_time
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


md = Model(domain_description=parsing.domain_description.parse_file("../example/lib.adl3"),
           scenario=parsing.scenario.parse_file("../example/scenario.txt"))
