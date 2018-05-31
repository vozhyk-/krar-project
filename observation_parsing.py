from typing import List

from observation import Observation
import condition_parsing


def parse(lines: List[str]):
    return list(map(parse_line, lines))

def parse_line(line: str) -> Observation:
    raw_begin_time, raw_condition = line.split(' ', 1)
    begin_time = int(raw_begin_time)
    condition = condition_parsing.parse(raw_condition)
    return Observation(condition, begin_time)
