import unittest
import sympy

import parsing.scenario
from structs.condition import Condition


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        scenario = parsing.scenario.parse_file("example/scenario.txt")

        assert len(scenario.observations) == 1
        assert scenario.observations[0].begin_time == 0

        alive, loaded = sympy.symbols("alive,loaded")
        expected_formula = alive & ~loaded
        assert scenario.observations[0].condition.formula == expected_formula

        assert len(scenario.action_occurrences) == 2

        assert scenario.action_occurrences[0].name == "Load"
        assert scenario.action_occurrences[0].begin_time == 1
        assert scenario.action_occurrences[0].duration == 2

        assert scenario.action_occurrences[1].name == "Shoot"
        assert scenario.action_occurrences[1].begin_time == 3
        assert scenario.action_occurrences[1].duration == 1
