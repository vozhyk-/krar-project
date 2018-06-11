from typing import List, Union
from structs.query import Query, ActionQuery, ScenarioQuery
import re


def parse_file(query_file: str) -> List[Query]:
    with open(query_file) as f:
        lines = f.readlines()
    queries = [parse_query(x.strip()) for x in lines]
    return queries


def parse_query(raw_query: str) -> Union[Query, None]:
    """
    words = raw_query.split(sep=' ')
    print('Words: ', words)
    # TODO maybe parse with regex...but if it works, it works?
    if "when" in words:
        # We have a ScenarioQuery
        query_type = words[0]
        if (query_type != "necessary") or (query_type != "possibly"):
            pass
    """
    action_regex = re.compile("(necessary|possibly) executable (.*?) in ([0-9]+)$")
    scenario_regex = re.compile("(necessary|possibly) (.*?) at ([0-9]+) when ([a-zA-Z0-9].*[a-zA-Z0-9]+)$")
    action_match = action_regex.search(raw_query)
    if action_match:
        print("Query:", raw_query, "matched action_regex, groups:", action_match.groups())
    else:
        scenario_match = scenario_regex.search(raw_query)
        if scenario_match:
            print("Query:", raw_query, "matched scenario_regex, groups:", scenario_match.groups())
    # return Query(raw_query)