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
    type_descriptions = [
        {
            "regex": re.compile("^([^ ]*) (causes|releases) (.*?)( if (.*))? during ([0-9]+)$"),
            "type": parse_effect_statement,
        },
        {
            "regex": re.compile("^impossible ([^ ]*) if (.*)$"),
            "type": parse_impossible_if,
        },
        {
            "regex": re.compile("^impossible ([^ ]*) at ([0-9]+)$"),
            "type": parse_impossible_at,
        },
    ]

    for desc in type_descriptions:
        match = desc["regex"].search(input)
        if match:
            return desc["type"](*match.groups())

def parse_effect_statement(raw_action, raw_statement_type,
    raw_effect, if_clause, raw_condition, raw_duration):

    statement_type = parse_statement_type(raw_statement_type)
    condition_args = parse_optional_condition_args(raw_condition)

    return statement_type(
        action=raw_action,
        effect=parsing.condition.parse(raw_effect),
        duration=int(raw_duration),
        **condition_args)

def parse_statement_type(raw_statement_type: str) -> type:
    if raw_statement_type == "causes":
        return Causes
    elif raw_statement_type == "releases":
        return Releases

def parse_optional_condition_args(raw_condition: str) -> dict:
    if raw_condition is None:
        return {}
    # Releases should have a single fluent,
    # but we just parse it as a formula anyway.
    condition = parsing.condition.parse(raw_condition)
    return {"condition": condition}

def parse_impossible_if(raw_action, raw_condition):
    return ImpossibleIf(raw_action, parsing.condition.parse(raw_condition))

def parse_impossible_at(raw_action, raw_time):
    return ImpossibleAt(raw_action, int(raw_time))
