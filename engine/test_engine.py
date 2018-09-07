import unittest
from engine.engine import Engine
import parsing.scenario
import parsing.domain_description


class EngineTestCase(unittest.TestCase):
    def test_one_model_case(self):
        scenario = parsing.scenario.parse_file("../test_models/one_model_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/one_model_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(1, len(engine.models))

    def test_fork_model_case(self):
        scenario = parsing.scenario.parse_file("../test_models/fork_model_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/fork_model_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(2, len(engine.models))

    def test_three_initial_model_case(self):
        scenario = parsing.scenario.parse_file("../test_models/three_initial_model_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/three_initial_model_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(3, len(engine.models))

    def test_model_destruction_impossibleif_case(self):
        scenario = parsing.scenario.parse_file("../test_models/model_destruction_impossibleif_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/model_destruction_impossibleif_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(0, len(engine.models))

    def test_model_destruction_impossibleat_case(self):
        scenario = parsing.scenario.parse_file("../test_models/model_destruction_impossibleat_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/model_destruction_impossibleat_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(0, len(engine.models))

    def test_model_destruction_observation_case(self):
        scenario = parsing.scenario.parse_file("../test_models/model_destruction_observation_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/model_destruction_observation_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(0, len(engine.models))

    def test_model_impossible_condition_case(self):
        scenario = parsing.scenario.parse_file("../test_models/model_impossible_condition_case_scenario.txt")
        domain = parsing.domain_description.parse_file("../test_models/model_impossible_condition_case_domain.txt")
        engine = Engine()
        engine.run(scenario, domain)
        self.assertEqual(1, len(engine.models))