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
            "regex": re.compile("^([^ ]*) causes (.*) during ([0-9]+)$"),
            "type": parse_causes,
        },
        {
            "regex": re.compile("^([^ ]*) releases (.*) during ([0-9]+)$"),
            "type": parse_releases,
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

def parse_causes(raw_action, raw_effect, duration):
    return Causes(
        action=raw_action,
        effect=parsing.condition.parse(raw_effect),
        duration=int(duration))

def parse_releases(*groups):
    return Releases()

def parse_impossible_if(raw_action, raw_condition):
    return ImpossibleIf(raw_action, parsing.condition.parse(raw_condition))

def parse_impossible_at(raw_action, raw_time):
    return ImpossibleAt(raw_action, int(raw_time))
