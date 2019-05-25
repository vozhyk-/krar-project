from typing import NamedTuple
from sympy.logic import boolalg


class Condition(NamedTuple):
    formula: boolalg.Boolean = True
