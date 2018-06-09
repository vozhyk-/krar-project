import re

from structs.statements import (
    Statement,
    Causes,
    Releases,
    ImpossibleIf,
    ImpossibleAt
)


def parse(input: str) -> Statement:
    type_descriptions = [
        {
            "regex": re.compile("^([^ ]*) causes (.*) during ([0-9]+)$"),
            "type": Causes,
        },
        {
            "regex": re.compile("^([^ ]*) releases (.*) during ([0-9]+)$"),
            "type": Releases,
        },
        {
            "regex": re.compile("^impossible ([^ ]*) if (.*)$"),
            "type": ImpossibleIf,
        },
        {
            "regex": re.compile("^impossible ([^ ]*) at ([0-9]+)$"),
            "type": ImpossibleAt,
        },
    ]

    for desc in type_descriptions:
        if desc["regex"].search(input):
            return desc["type"]()
