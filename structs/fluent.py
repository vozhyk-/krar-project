from typing import NamedTuple


class Fluent(NamedTuple):
    name: str
    value: bool

    def __str__(self):
        return self.name + " is " + str(self.value)
