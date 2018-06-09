import unittest

import parsing.scenario_parser
from structs.condition import Condition


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        scenario = parsing.scenario_parser.parse("example/scenario.txt")

        assert len(scenario.observations) == 1
        assert scenario.observations[0].begin_time == 0
        assert isinstance(scenario.observations[0].condition, Condition)

        assert len(scenario.action_occurences) == 2
