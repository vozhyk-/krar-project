import unittest
import sympy

import parsing.statement
from structs.statements import (
    Causes,
    ImpossibleAt,
    ImpossibleIf
)
from structs.condition import Condition


class StatementParsingTestCase(unittest.TestCase):
    def test_impossible_at(self):
        statement = parsing.statement.parse("impossible Work at 14")
        self.assertEqual(statement, ImpossibleAt(action="Work", time=14))

    def test_impossible_if(self):
        statement = parsing.statement.parse("impossible Work if sick | dead")
        expected_condition = parsing.condition.parse("sick | dead")
        self.assertEqual(statement,
            ImpossibleIf(action="Work", condition=expected_condition))

    def test_unconditional_causes(self):
        statement = parsing.statement.parse("Charge causes charged during 6")
        charged = sympy.symbols("charged")
        self.assertEqual(statement,
            Causes(action="Charge", effect=Condition(charged), duration=6))
