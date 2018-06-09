from typing import List

from structs.observation import Observation
import parsing.condition


def parse_all(lines: List[str]):
    return list(map(parse, lines))

def parse(line: str) -> Observation:
    raw_begin_time, raw_condition = line.split(' ', 1)
    begin_time = int(raw_begin_time)
    condition = parsing.condition.parse(raw_condition)
    return Observation(condition, begin_time)
