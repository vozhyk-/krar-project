from structs.condition import Condition
from typing import List


class Query:
    def validate(self, structure) -> bool:
        return True


class ActionQuery(Query):
    def __init__(self, actions: List[str], duration: int):
        self.actions = actions


class ScenarioQuery(Query):
    def __init__(self, condition: Condition, is_necessary: bool, ):
        self.condition = condition
