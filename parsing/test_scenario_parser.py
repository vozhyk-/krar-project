import unittest

from scenario_parser import ScenarioParser
from condition import Condition
import condition_parsing


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        parser = ScenarioParser()
        scenario = parser.parse("example/scenario.txt")

        assert len(scenario.observations) == 1
        assert scenario.observations[0].begin_time == 0
        assert isinstance(scenario.observations[0].condition, Condition)

        assert len(scenario.action_occurences) == 2
