from typing import List

from structs.statements import Statement


class DomainDescription:
    def __init__(self, statements: List[Statement]):
        self.statements = statements
