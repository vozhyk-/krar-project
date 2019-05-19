from typing import List

from structs.action_occurrence import ActionOccurrence


def parse_all(lines: List[str]) -> List[ActionOccurrence]:
    return list(map(parse, lines))


def parse(line: str) -> ActionOccurrence:
    name, agent_name, raw_begin_time = line.split(" ")
    return ActionOccurrence(name=name, begin_time=int(raw_begin_time), duration=1, agent=agent_name)
