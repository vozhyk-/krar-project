from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from structs.fluent import Fluent
from structs.action_occurrence import ActionOccurrence
import parsing.domain_description, parsing.scenario
from sympy import Symbol, Not, Or, And
from sympy.logic.inference import satisfiable


class Model:
    def __init__(self, domain_description: DomainDescription, scenario: Scenario):
        self.domain_description = domain_description
        self.scenario = scenario
        self.fluents = self.parse_fluents()
        self.consistent = False

    def history_function(self, fluents: Fluent, time_point: int):
        pass

    def occlusion_function(self, action: ActionOccurrence, time_point: int):
        pass

    def actions_occurence_relation(self, action: ActionOccurrence, time_point: int):
        pass

    def parse_fluents(self):
        fluents = []
        for observation in self.scenario.observations:
            if observation.begin_time == 0:
                for key, value in satisfiable(observation.condition.formula).items():
                    fluents.append(Fluent(key.name, value))

        return fluents


md = Model(domain_description=parsing.domain_description.parse_file("../example/lib.adl3"),
           scenario=parsing.scenario.parse_file("../example/scenario.txt"))
