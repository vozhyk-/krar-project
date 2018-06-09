import re

from structs.statements import (
    Statement,
    Causes,
    Releases,
    ImpossibleIf,
    ImpossibleAt
)


def parse(input: str) -> Statement:
    causes_regex = re.compile("^([^ ]*) causes (.*) during ([0-9]+)$")
    releases_regex = re.compile("^([^ ]*) releases (.*) during ([0-9]+)$")
    impossible_if_regex = re.compile("^impossible ([^ ]*) if (.*)$")
    impossible_at_regex = re.compile("^impossible ([^ ]*) at ([0-9]+)$")

    if causes_regex.search(input):
        return Causes()
    elif releases_regex.search(input):
        return Releases()
    elif impossible_if_regex.search(input):
        return ImpossibleIf()
    elif impossible_at_regex.search(input):
        return ImpossibleAt()
