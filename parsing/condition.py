import sympy.parsing.sympy_parser as sympy_parser

from structs.condition import Condition


def parse(input: str) -> Condition:
    return Condition(sympy_parser.parse_expr(input))
