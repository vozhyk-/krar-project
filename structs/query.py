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
    def __init__(self, query_type: str, actions: str, begin_time: int, duration: str = 1):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.action_strings = actions.split(',')
        self.action_strings = [act.lower() for act in self.action_strings]
        self.duration = int(duration)
        self.time_point = begin_time
        self.str = "{} {} at {}".format(query_type, self.action_strings[0], str(begin_time))

    def validate(self, models: List[Model], scen: Scenario = None) -> bool:
        if len(models) == 0:
            return True

        #scenario_act_names = [act.name.lower() for act in scen.action_occurrences]
        #for action_str in self.action_strings:
        #    if action_str not in scenario_act_names:
        #        print("Action:", action_str, " is not in the scenario!")
        #        return False
        # print('self.action_strings:', self.action_strings)
        is_valid = False
        if self.query_type == QueryType.POSSIBLY:
            for model in models:
                is_valid = False
                model_action_strings = [act.name.lower() for act in model.action_history.values()]
                for act_str in self.action_strings:
                    if act_str not in model_action_strings:
                        break
                # TODO simplify logic
                t = self.time_point
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

        elif self.query_type == QueryType.NECESSARY:
            for model in models:
                is_valid = False
                model_action_strings = [act.name.lower() for act in model.action_history.values()]
                for act_str in self.action_strings:
                    if act_str not in model_action_strings:
                        return False
                # TODO simplify logic
                t = self.time_point
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

        return is_valid

    def __str__(self):
        return self.str


class ConditionQuery(Query):
    def __init__(self, query_type: str, condition_str: str, time_point: str, scenario: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.condition = parsing.condition.parse(condition_str)
        self.time_point = int(time_point)
        self.str = self.str = "{} {} at {} when {}".format(self.query_type, str(self.condition), self.time_point, scenario)

    def validate(self,  models: List[Model], scen: Scenario = None) -> bool:
        if len(models) == 0:
            return True

        evaluations = []
        for i in range(len(models) - 1, -1, -1):
            expr, expr_values = models[i].get_symbol_values(self.time_point)
            evaluations.append(InconsistencyChecker.evaluate(expr, expr_values, self.condition.formula))
        if self.query_type == QueryType.POSSIBLY:
            return self.evaluate_possible_query(evaluations)
        else:
            return self.evaluate_necessary_query(evaluations)

    def evaluate_possible_query(self, evaluations: List[bool]) -> bool:
        print("Evaluations: ", evaluations)
        return any(x!=False for x in evaluations)

    def evaluate_necessary_query(self, evaluations: List[bool]) -> bool:
        print("Evaluations: ", evaluations)
        return all(x==True for x in evaluations)

    def __str__(self):
        return self.str


class InvolvedQuery(Query):
    def __init__(self, query_type: str, agent: str):
        self.query_type = QueryType.NECESSARY if query_type == "necessary" else QueryType.POSSIBLY
        self.agent = agent
        self.str = "{} involved {} ".format(self.query_type, self.agent)

    def validate(self,  models: List[Model], scen: Scenario = None) -> bool:
        if len(models) == 0:
            # If no models then agent surely was not involved?
            return True

        for model in models:
            agent_involved_in_model = False
            for action in model.action_history.values():
                if action.agent == self.agent and self.query_type == QueryType.POSSIBLY:
                    return True
                elif action.agent == self.agent:
                    agent_involved_in_model = True
                    break
            if not agent_involved_in_model and self.query_type == QueryType.NECESSARY:
                return False

        return True

    def __str__(self):
        return self.str
