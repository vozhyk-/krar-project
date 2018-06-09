import re

from structs.statements import Statement, Causes, Releases, ImpossibleIf


def parse(input: str) -> Statement:
    causes_regex = re.compile("^([^ ]*) causes (.*) during ([0-9]+)$")
    releases_regex = re.compile("^([^ ]*) releases (.*) during ([0-9]+)$")
    impossible_if_regex = re.compile("^impossible ([^ ]*) if (.*)$")

    if causes_regex.search(input):
        return Causes()
    elif releases_regex.search(input):
        return Releases()
    elif impossible_if_regex.search(input):
        return ImpossibleIf()
