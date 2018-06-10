import re

from structs.statements import (
    Statement,
    Causes,
    Releases,
    ImpossibleIf,
    ImpossibleAt
)
import parsing.condition


def parse(input: str) -> Statement:
    types = [
        EffectStatementParser,
        ImpossibleIfParser,
        ImpossibleAtParser,
    ]

    for t in types:
        match = t.regex.search(input)
        if match:
            return t.parse_groups(*match.groups())


class EffectStatementParser:
    regex = re.compile("^([^ ]*) (causes|releases) (.*?)( if (.*))? during ([0-9]+)$")

    @staticmethod
    def parse_groups(raw_action, raw_statement_type,
                     raw_effect, if_clause, raw_condition, raw_duration):

        statement_type = EffectStatementParser.parse_statement_type(raw_statement_type)
        condition_args = EffectStatementParser.parse_optional_condition_args(raw_condition)

        return statement_type(
            action=raw_action,
            effect=parsing.condition.parse(raw_effect),
            duration=int(raw_duration),
            **condition_args)

    @staticmethod
    def parse_statement_type(raw_statement_type: str) -> type:
        if raw_statement_type == "causes":
            return Causes
        elif raw_statement_type == "releases":
            return Releases

    @staticmethod
    def parse_optional_condition_args(raw_condition: str) -> dict:
        if raw_condition is None:
            return {}
        # Releases should have a single fluent,
        # but we just parse it as a formula anyway.
        condition = parsing.condition.parse(raw_condition)
        return {"condition": condition}


class ImpossibleIfParser:
    regex = re.compile("^impossible ([^ ]*) if (.*)$")

    @staticmethod
    def parse_groups(raw_action, raw_condition):
        return ImpossibleIf(raw_action, parsing.condition.parse(raw_condition))


class ImpossibleAtParser:
    regex = re.compile("^impossible ([^ ]*) at ([0-9]+)$")

    @staticmethod
    def parse_groups(raw_action, raw_time):
        return ImpossibleAt(raw_action, int(raw_time))
