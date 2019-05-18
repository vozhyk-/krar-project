import unittest
import sympy
import parsing.domain_description
import os
from structs.statements import Causes, Releases, Triggers
from structs.condition import Condition


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        description = parsing.domain_description.parse_file("../example/lib.adl3")

        self.assertEqual(len(description.statements), 5)

        alive, loaded, hidden = sympy.symbols("alive,loaded,hidden")
        #####
        self.assertTrue(isinstance(description.statements[0], Causes))
        self.assertEqual(Causes(
            action="load", effect=Condition(loaded), agent="hunter"), description.statements[0])
        #####
        self.assertTrue(isinstance(description.statements[1], Causes))
        self.assertEqual(Causes(
            action="shoot", effect=Condition(~loaded), agent="hunter"), description.statements[1])
        #####
        self.assertTrue(isinstance(description.statements[2], Causes))
        self.assertEqual(Causes(
            action="shoot", effect=Condition(~alive), condition=Condition(loaded & ~hidden), agent="hunter"),
            description.statements[2])
        #####
        self.assertTrue(isinstance(description.statements[3], Releases))
        self.assertEqual(Releases(
            action="escape",
            effect=Condition(hidden), agent="turkey"), description.statements[3])
        #####
        self.assertTrue(isinstance(description.statements[4], Triggers))
        self.assertEqual(Triggers(
            action="escape", condition=Condition(loaded)), description.statements[4])
