from structs.domain_description import DomainDescription
from structs.scenario import Scenario
from structs.action_occurrence import ActionOccurrence
from structs.observation import Observation
from structs.statements import Statement, EffectStatement, ImpossibleAt, ImpossibleIf
from typing import List


class Preprocessor:
    def remove_duplicates(self, domain_description: DomainDescription, scenario: Scenario):
        unique_domain = self.remove_duplicated_statements(domain_description)
        unique_obs = self.remove_duplicated_observations(scenario.observations)
        unique_actions = self.remove_duplicated_actions(scenario.action_occurrences)
        unique_scenario = Scenario(unique_obs, unique_actions)
        return unique_domain, unique_scenario

    def remove_duplicated_statements(self, domain_description: DomainDescription):
        unique_stat = []
        for i in range(len(domain_description.statements)):
            if self.is_unique(unique_stat, domain_description.statements[i]):
                unique_stat.append(domain_description.statements[i])
        return DomainDescription(unique_stat)

    def is_unique(self, unique_stat: List[Statement], statement: Statement):
        if isinstance(statement, EffectStatement):
            for j in range(len(unique_stat)):
                if (isinstance(unique_stat[j], EffectStatement)
                        and (statement.action == unique_stat[j].action)
                        and (statement.duration == unique_stat[j].duration)
                        and (statement.condition == unique_stat[j].condition)
                        and (statement.effect == unique_stat[j].effect)):
                    return False

        if isinstance(statement, ImpossibleIf):
            for j in range(len(unique_stat)):
                if (isinstance(unique_stat[j], ImpossibleIf)
                        and (statement.action == unique_stat[j].action)
                        and (statement.condition == unique_stat[j].condition)):
                    return False

        if isinstance(statement, ImpossibleAt):
            for j in range(len(unique_stat)):
                if (isinstance(unique_stat[j], ImpossibleAt)
                        and (statement.action == unique_stat[j].action)
                        and (statement.time == unique_stat[j].time)):
                    return False
        return True

    def remove_duplicated_observations(self, observations: List[Observation]):
        unique_obs = []
        for i in range(len(observations)):
            unique = True
            for j in range(len(unique_obs)):
                if ((observations[i].condition == unique_obs[j].condition)
                        and (observations[i].begin_time == unique_obs[j].begin_time)):
                    unique = False
                    break
            if unique:
                unique_obs.append(observations[i])
        return unique_obs

    def remove_duplicated_actions(self, actions: List[ActionOccurrence]):
        unique_act = []
        for i in range(len(actions)):
            unique = True
            for j in range(len(unique_act)):
                if ((actions[i].duration == unique_act[j].duration)
                        and (actions[i].begin_time == unique_act[j].begin_time)
                        and (actions[i].name == unique_act[j].name)):
                    unique = False
                    break
            if unique:
                unique_act.append(actions[i])
        return unique_act
