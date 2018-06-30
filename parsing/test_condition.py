import unittest
import sympy
import parsing.condition


class ConditionParsingTestCase(unittest.TestCase):
    def test_or(self):
        condition = parsing.condition.parse("sick | dead")
        sick, dead = sympy.symbols("sick,dead")
        assert condition.formula == sick | dead

    def test_and_not(self):
        condition = parsing.condition.parse("~loaded & ~alive")
        loaded, alive = sympy.symbols("loaded,alive")
        assert condition.formula == ~loaded & ~alive
