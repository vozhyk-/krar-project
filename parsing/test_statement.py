import unittest
import sympy

import parsing.statement
from structs.statements import (
    Causes,
    Releases,
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

    def test_conditional_causes(self):
        statement = parsing.statement.parse("Charge causes charged if plugged_in during 6")
        charged, plugged_in = sympy.symbols("charged,plugged_in")
        self.assertEqual(statement,
            Causes(
                action="Charge",
                effect=Condition(charged),
                condition=Condition(plugged_in),
                duration=6))

    def test_unconditional_releases(self):
        statement = parsing.statement.parse("Use releases broken during 14")
        broken = sympy.symbols("broken")
        self.assertEqual(statement,
             Releases(
                 action="Use",
                 effect=Condition(broken),
                 duration=14))

    def test_conditional_releases(self):
        statement = parsing.statement.parse("Use releases broken if unlucky during 14")
        broken, unlucky = sympy.symbols("broken,unlucky")
        self.assertEqual(statement,
             Releases(
                 action="Use",
                 effect=Condition(broken),
                 condition=Condition(unlucky),
                 duration=14))
