from structs.condition import Condition
from typing import List
from enum import Enum
from engine.model import Model
import parsing.condition
from engine.inconsistency_checker import InconsistencyChecker
from structs.scenario import Scenario


class QueryType(Enum):
    NECESSARY = 1
    POSSIBLY = 2


class Query:
    # To be overridden
    def validate(self, models: List[Model], scen: Scenario = None) -> bool:
        return True


class ActionQuery(Query):
    def __init__(self, query_type: str, actions: str, duration: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.action_strings = actions.split(',')
        self.action_strings = [act.lower() for act in self.action_strings]
        self.duration = int(duration)
        self.str = query_type + " executable " + actions + " in " + duration

    def validate(self, models: List[Model], scen: Scenario = None) -> bool:
        scenario_act_names = [act.name.lower() for act in scen.action_occurrences]
        for action_str in self.action_strings:
            if action_str not in scenario_act_names:
                print("Action:", action_str, " is not in the scenario!")
                return False
        # print('self.action_strings:', self.action_strings)
        is_valid = False
        if self.query_type == QueryType.POSSIBLY:
            for model in models:
                is_valid = False
                model_action_strings = [act.name.lower() for act in model.action_history.values()]
                for act_str in self.action_strings:
                    if act_str not in model_action_strings:
                        break
                t = 0
                while t < model.last_time_point:
                    for i in range(len(self.action_strings)):
                        if t in model.action_history.keys() and model.action_history[t].name.lower() == self.action_strings[i]:
                            # found first action
                            end_time = model.action_history[t].begin_time + self.duration
                            t = model.action_history[t].begin_time + model.action_history[t].duration
                            if t > end_time:
                                # first action's duration is too long
                                break
                            elif len(self.action_strings) == 1:
                                # print('is_valid = True')
                                return True
                            final_idx = len(self.action_strings) - 1 if i != len(self.action_strings) - 1 else len(self.action_strings) - 2
                            while t < end_time:
                                for j in range(len(self.action_strings)):
                                    if i != j:
                                        if t in model.action_history.keys() and model.action_history[t].name.lower() == self.action_strings[j]:
                                            t += model.action_history[t].duration
                                            if t > end_time:
                                                # i = -1
                                                break
                                            elif j == final_idx:
                                                # valid interval found
                                                return True
                                t += 1
                    t += 1

        elif self.query_type == QueryType.NECESSARY:
            for model in models:
                is_valid = False
                model_action_strings = [act.name.lower() for act in model.action_history.values()]
                for act_str in self.action_strings:
                    if act_str not in model_action_strings:
                        return False
                t = 0
                while t < model.last_time_point:
                    for i in range(len(self.action_strings)):
                        if t in model.action_history.keys() and model.action_history[t].name.lower() == self.action_strings[i]:
                            # found first action
                            end_time = model.action_history[t].begin_time + self.duration
                            t = model.action_history[t].begin_time + model.action_history[t].duration
                            if t > end_time:
                                # first action's duration is too long
                                break
                            elif len(self.action_strings) == 1:
                                # print('is_valid = True')
                                is_valid = True
                            final_idx = len(self.action_strings) - 1 if i != len(self.action_strings) - 1 else len(self.action_strings) - 2
                            while t < end_time:
                                for j in range(len(self.action_strings)):
                                    if i != j:
                                        if t in model.action_history.keys() and model.action_history[t].name.lower() == self.action_strings[j]:
                                            t += model.action_history[t].duration
                                            if t > end_time:
                                                # i = -1
                                                break
                                            elif j == final_idx:
                                                # valid interval found
                                                is_valid = True
                                t += 1
                    t += 1
                if not is_valid:
                    return False
        return is_valid

    def __str__(self):
        return self.str


class ScenarioQuery(Query):
    def __init__(self, query_type: str, condition_str: str, time_point: str, scenario_file: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.condition = parsing.condition.parse(condition_str)
        self.time_point = int(time_point)
        self.scenario_file = scenario_file
        self.str = query_type + " " + str(self.condition.formula) + " at " + time_point + " when " + scenario_file

    def validate(self,  models: List[Model], scen: Scenario = None) -> bool:
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