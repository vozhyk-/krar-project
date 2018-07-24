from structs.condition import Condition
from typing import List
from enum import Enum
from engine.model import Model
import parsing.condition
from engine.inconsistency_checker import InconsistencyChecker


class QueryType(Enum):
    NECESSARY = 1
    POSSIBLY = 2


class Query:
    # To be overridden
    def validate(self, models: List[Model]) -> bool:
        return True


class ActionQuery(Query):
    def __init__(self, query_type: str, actions: str, duration: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.actions = actions.split(',')
        self.duration = int(duration)
        self.str = query_type + " executable " + actions + " in " + duration

    def validate(self, models: List[Model]) -> bool:
        # TODO add a list of tuples of actions -> time of action being executed,
        #  and for a given duration check if each action is in the list
        return super().validate(models)

    def __str__(self):
        return self.str


class ScenarioQuery(Query):
    def __init__(self, query_type: str, condition_str: str, time_point: str, scenario_file: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.condition = parsing.condition.parse(condition_str)
        self.time_point = int(time_point)
        self.scenario_file = scenario_file
        self.str = query_type + " " + str(self.condition.formula) + " at " + time_point + " when " + scenario_file

    def validate(self,  models: List[Model]) -> bool:
        for i in range(len(models) - 1, -1, -1):
            expr, expr_values = models[i].get_symbol_values(self.time_point)
            evaluation = InconsistencyChecker.evaluate(expr, expr_values, self.condition.formula)
            # If this is a POSSIBLY query and our query holds in at least 1 model, return True
            if self.query_type == QueryType.POSSIBLY and evaluation:
                return True
            # If this is a NECESSARY query and in 1 model our query doesn't hold, return False
            elif self.query_type == QueryType.NECESSARY and not evaluation:
                return False
            # If this is a NECESSARY query and we already checked all models (i == 0) then return True
            elif self.query_type == QueryType.NECESSARY and evaluation and i == 0:
                return True
        # If this is a POSSIBLY query and our query doesn't hold in any model, return False
        return False

    def __str__(self):
        return self.str