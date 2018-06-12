from structs.condition import Condition
from typing import List
from enum import Enum
import parsing.condition


class QueryType(Enum):
    NECESSARY = 1
    POSSIBLY = 2


class Query:
    # To be overridden
    def validate(self, structure) -> bool:
        return True


class ActionQuery(Query):
    def __init__(self, query_type: str, actions: str, duration: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.actions = actions.split(',')
        self.duration = int(duration)


class ScenarioQuery(Query):
    def __init__(self, query_type: str, condition_str: str, time_point: str, scenario_file: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.condition = parsing.condition.parse(condition_str)
        self.time_point = int(time_point)
        self.scenario_file = scenario_file
