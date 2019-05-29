import re

from structs.statements import (
    Statement,
    Causes,
    Releases,
    ImpossibleIf,
    ImpossibleAt,
    ImpossibleBy,
    Triggers
)
import parsing.condition


def parse(input: str) -> Statement:
    types = [
        EffectStatementAgentParser,
        EffectStatementParser,
        ImpossibleIfParser,
        ImpossibleByParser,
        TriggersParser,
        TriggersAgentParser
    ]

    for t in types:
        match = t.regex.search(input)
        if match:
            return t.parse_groups(*match.groups())


def parse_statement_type(raw_statement_type: str) -> type:
    if raw_statement_type == "causes":
        return Causes
    elif raw_statement_type == "releases":
        return Releases


class EffectStatementAgentParser:
    regex = re.compile("^([^ ]*) (causes|releases) (.*?)( if (.*))? by ([^ ]*)$")

    @staticmethod
    def parse_groups(raw_action, raw_statement_type,
                     raw_effect, if_clause, raw_condition, agent):
        statement_type = parse_statement_type(raw_statement_type)
        # condition_args = EffectStatementAgentParser.parse_optional_condition_args(raw_condition)

        return statement_type(
            action=raw_action,
            effect=parsing.condition.parse(raw_effect),
            condition=parsing.condition.parse(raw_condition),
            agent=agent,
            )

    # @staticmethod
    # def parse_optional_condition_args(raw_condition: str) -> dict:
    #     if raw_condition is None:
    #         return {}
    #     # Releases should have a single fluent,
    #     # but we just parse it as a formula anyway.
    #     condition = parsing.condition.parse(raw_condition)
    #     return {"condition": condition}


class EffectStatementParser:
    regex = re.compile("^([^ ]*) (causes|releases) (.*?)( if (.*))?$")

    @staticmethod
    def parse_groups(raw_action, raw_statement_type,
                     raw_effect, if_clause, raw_condition):
        statement_type = parse_statement_type(raw_statement_type)
        # condition_args = EffectStatementAgentParser.parse_optional_condition_args(raw_condition)

        return statement_type(
            action=raw_action,
            effect=parsing.condition.parse(raw_effect),
            condition=parsing.condition.parse(raw_condition),
            agent='nobody',
            )


class ImpossibleIfParser:
    regex = re.compile("^impossible ([^ ]*) if (.*)$")

    @staticmethod
    def parse_groups(raw_action, raw_condition):
        return ImpossibleIf(raw_action, parsing.condition.parse(raw_condition))


# TODO remove
class ImpossibleAtParser:
    regex = re.compile("^impossible ([^ ]*) at ([0-9]+)$")

    @staticmethod
    def parse_groups(raw_action, raw_time):
        return ImpossibleAt(raw_action, int(raw_time))


class ImpossibleByParser:
    regex = re.compile("^impossible ([^ ]*) by ([^ ]*)$")

    @staticmethod
    def parse_groups(raw_action, agent):
        return ImpossibleBy(action=raw_action, agent=agent)


class TriggersParser:
    regex = re.compile("^([^ ]*) triggers ([^ ]*)$")

    @staticmethod
    def parse_groups(raw_condition, raw_action):
        return Triggers(condition=parsing.condition.parse(raw_condition), action=raw_action, agent='nobody')

class TriggersAgentParser:
    regex = re.compile("^([^ ]*) triggers ([^ ]*) by ([^ ]*)$")

    @staticmethod
    def parse_groups(raw_condition, raw_action, agent):
        return Triggers(condition=parsing.condition.parse(raw_condition), action=raw_action, agent=agent)