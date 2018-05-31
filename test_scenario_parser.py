import unittest

from scenario_parser import ScenarioParser


class ScenarioParserTestCase(unittest.TestCase):
    def test_test(self):
        parser = ScenarioParser()
        scenario = parser.parse("example/scenario.txt")

        assert len(scenario.observations) == 1
        assert len(scenario.action_occurences) == 2
