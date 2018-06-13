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
        self.is_consistent = True
        last_action = self.scenario.action_occurrences[-1]
        self.last_time_point = last_action.begin_time + last_action.duration + 1
        self.fluent_history = self.initialize_history()
        self.prev_time_point = 0

    def initialize_history(self) -> ndarray:
        fluent_history = ndarray(shape=(self.last_time_point, len(self.fluents)), dtype=Fluent)
        for i in range(len(self.fluents)):
            fluent_history[0][i] = self.fluents[i]
        return fluent_history

    def history_function(self, fluent: Fluent, time_point: int) -> bool:
        time_point_row = self.fluent_history[time_point]
        return time_point_row.__contains__(fluent)

    def occlusion_function(self, action: ActionOccurrence, time_point: int = None):
        fluents_under_influence = []
        start_time = time_point if 0 <= time_point < action.begin_time else action.begin_time
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

    #TODO execution of the action
    def execute(self, action: ActionOccurrence):
        self.inertia_law(action.begin_time)
        #do to something
        pass

    def inertia_law(self, time_point: int):
        for i in range(len(self.fluents)):
            for j in range(self.prev_time_point, time_point):
                self.fluent_history[j][i] = self.fluent_history[self.prev_time_point][i]
        self.prev_time_point = time_point

    def fork_model(self, time_point: int):
        model = Model(self.domain_description, self.scenario)
        for i in range(len(self.fluents)):
            for j in range(0, time_point):
                model.fluent_history[j][i] = self.fluent_history[j][i]
        model.prev_time_point = time_point
        return model

    def invalidate_model(self):
        self.is_consistent = False
