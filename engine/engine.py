from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from engine.model import Model
from structs.action_occurrence import ActionOccurrence
from structs.observation import Observation
from structs.statements import Statement, EffectStatement, ImpossibleAt, ImpossibleIf
from typing import List


class Engine:
    def __init__(self, domain_description: DomainDescription, scenario: Scenario):
        self.domain_description = domain_description
        self.scenario = scenario
        self.models = []

    def create_models(self):
        for action in self.scenario.action_occurrences:
            statements = self.get_statements_for_action(action)
            #for model in self.models:
                #if statement is executable
                #execute -> update history function
                #
                #model.execute(action)
        pass

    def get_statements_for_action(self, action: ActionOccurrence):
        statements = []
        for statement in self.domain_description.statements:
            if isinstance(statement, EffectStatement):
                if ((statement.action == action.name)
                and (statement.duration <= action.duration)):
                    statements.append(statement)
        return statements