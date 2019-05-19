from typing import List, Union
from structs.query import Query, ActionQuery, ConditionQuery, InvolvedQuery
import re


def parse_file(query_file: str) -> List[Query]:
    with open(query_file) as f:
        lines = f.readlines()
    queries = [parse_query(x.strip()) for x in lines]
    queries = [x for x in queries if x is not None]  # remove None values
    return queries


def parse_text(text: str) -> List[Query]:
    lines = text.split('\n')
    lines = list(filter(None, lines))
    queries = [parse_query(x.strip()) for x in lines]
    queries = [x for x in queries if x is not None]  # remove None values
    return queries


def parse_query(raw_query: str) -> Union[Query, None]:
    action_regex = re.compile("(necessary|possibly) (.*?) at ([0-9]+)$")
    # We need "when Sc" in order to distinguish ActionQuery from ConditionQuery?
    condition_regex = re.compile("(necessary|possibly) (.*?) at ([0-9]+) when ([a-zA-Z0-9].*[a-zA-Z0-9]+)$")
    involved_regex = re.compile("(necessary|possibly) involved (.*?)$")
    action_match = action_regex.search(raw_query)
    condition_match = condition_regex.search(raw_query)
    involved_match = involved_regex.search(raw_query)
    if action_match:
        # print("Query:", raw_query, "matched action_regex, groups:", action_match.groups())
        return ActionQuery(*action_match.groups())
    elif condition_match:
        return ConditionQuery(*condition_match.groups())
    elif involved_match:
        return InvolvedQuery(*involved_match.groups())
    return None
