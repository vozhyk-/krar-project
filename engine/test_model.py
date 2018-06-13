import unittest

from engine.model import Model
from structs.fluent import Fluent
import parsing


class ModelTestCase(unittest.TestCase):
    def test_example(self):
        model = Model(
            domain_description=parsing.domain_description.parse_file("example/lib.adl3"),
            scenario=parsing.scenario.parse_file("example/scenario.txt"))

        self.assertTrue(model.history_function(Fluent("loaded", False), 0))
