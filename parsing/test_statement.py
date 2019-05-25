import unittest
import sympy

import parsing.statement
from structs.statements import (
    Causes,
    Releases,
    ImpossibleIf,
    ImpossibleBy,
    Triggers
)
from structs.condition import Condition


class StatementParsingTestCase(unittest.TestCase):

    def test_impossible_if(self):
        statement = parsing.statement.parse("impossible Work if sick | dead")
        expected_condition = parsing.condition.parse("sick | dead")
        self.assertEqual(ImpossibleIf(action="Work", condition=expected_condition), statement)

    def test_unconditional_causes(self):
        statement = parsing.statement.parse("Charge causes charged by Kuba")
        charged = sympy.symbols("charged")
        self.assertEqual(Causes(action="Charge", effect=Condition(charged), agent="Kuba"), statement)

    def test_conditional_causes(self):
        statement = parsing.statement.parse("Charge causes charged if plugged_in by Teddy")
        charged, plugged_in = sympy.symbols("charged,plugged_in")
        self.assertEqual(Causes(
            action="Charge",
            effect=Condition(charged),
            condition=Condition(plugged_in), agent="Teddy"), statement)

    def test_unconditional_releases(self):
        statement = parsing.statement.parse("Use releases broken by lol")
        broken = sympy.symbols("broken")
        self.assertEqual(Releases(
            action="Use",
            effect=Condition(broken), agent="lol"), statement)

    def test_conditional_releases(self):
        statement = parsing.statement.parse("Use releases broken if unlucky by lol")
        broken, unlucky = sympy.symbols("broken,unlucky")
        self.assertEqual(Releases(
            action="Use",
            effect=Condition(broken),
            condition=Condition(unlucky), agent="lol"), statement)

    def test_impossible_by(self):
        statement = parsing.statement.parse("impossible work by Kuba")
        self.assertEqual(ImpossibleBy(
            action="work", agent="Kuba"), statement)

    def test_triggers(self):
        statement = parsing.statement.parse("detonate triggers explosion")
        detonate = sympy.symbols("detonate")
        self.assertEqual(Triggers(
            action="explosion", condition=Condition(detonate)), statement)
