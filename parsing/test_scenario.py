import unittest
import sympy

import parsing.scenario
import parsing.condition
from structs.observation import Observation
from structs.action_occurrence import ActionOccurrence
from structs.condition import Condition


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        scenario = parsing.scenario.parse_file("example/scenario.txt")

        self.assertEqual(len(scenario.observations), 2)

        alive, loaded, hidden = sympy.symbols("alive,loaded,hidden")
        self.assertEqual(scenario.observations[0], Observation(
            begin_time=0,
            condition=Condition(alive & ~loaded & ~hidden)))
        self.assertEqual(scenario.observations[1], Observation(
            begin_time=1,
            condition=Condition(~alive & loaded & hidden)))

        self.assertEqual(len(scenario.action_occurrences), 2)
        self.assertEqual(scenario.action_occurrences[0],
                         ActionOccurrence(name="Load", begin_time=1, duration=2))
        self.assertEqual(scenario.action_occurrences[1],
                         ActionOccurrence(name="Shoot", begin_time=3, duration=1))
