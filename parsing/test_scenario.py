import unittest
import sympy

import parsing.scenario
from structs.condition import Condition


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        scenario = parsing.scenario.parse("example/scenario.txt")

        assert len(scenario.observations) == 1
        assert scenario.observations[0].begin_time == 0

        alive, loaded = sympy.symbols("alive,loaded")
        expected_formula = alive & ~loaded
        assert scenario.observations[0].condition.formula == expected_formula

        assert len(scenario.action_occurences) == 2
