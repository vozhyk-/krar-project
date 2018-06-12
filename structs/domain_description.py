from typing import NamedTuple, List

from structs.statements import Statement


class DomainDescription(NamedTuple):
    statements: List[Statement]
