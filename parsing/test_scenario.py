import unittest
import sympy
import os
import parsing.scenario
import parsing.condition
from structs.observation import Observation
from structs.action_occurrence import ActionOccurrence
from structs.condition import Condition

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        scenario = parsing.scenario.parse_file("../example/scenario.txt")

        self.assertEqual(len(scenario.observations), 1)

        alive, loaded, hidden = sympy.symbols("alive,loaded,hidden")
        self.assertEqual(Observation(begin_time=0, condition=Condition(alive & ~loaded & ~hidden)), scenario.observations[0])

        self.assertEqual(2, len(scenario.action_occurrences))
        self.assertEqual(ActionOccurrence(name="load", begin_time=1, agent="hunter"), scenario.action_occurrences[0])
        self.assertEqual(ActionOccurrence(name="shoot", begin_time=3, agent="hunter"), scenario.action_occurrences[1])
