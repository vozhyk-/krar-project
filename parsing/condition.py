import sympy.parsing.sympy_parser as sympy_parser
from typing import Union
from structs.condition import Condition


def parse(input: str) -> Union[Condition, bool]:
    if input is None:
        return True
    return Condition(sympy_parser.parse_expr(input))
