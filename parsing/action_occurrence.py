from typing import List

from structs.action_occurrence import ActionOccurrence


def parse_all(lines: List[str]) -> List[ActionOccurrence]:
    return list(map(parse, lines))


def parse(line: str) -> ActionOccurrence:
    name, raw_begin_time, raw_duration = line.split(" ")
    begin_time = int(raw_begin_time)
    duration = int(raw_duration)
    return ActionOccurrence(name, begin_time, duration)
