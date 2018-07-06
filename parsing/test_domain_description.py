import unittest
import sympy
import parsing.domain_description
from structs.statements import Causes, Releases, ImpossibleIf, ImpossibleAt
from structs.condition import Condition


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        description = parsing.domain_description.parse_file("example/lib.adl3")

        self.assertEqual(len(description.statements), 5)

        alive, loaded, hidden = sympy.symbols("alive,loaded,hidden")
        self.assertTrue(isinstance(description.statements[0], Releases))
        self.assertEqual(description.statements[0], Releases(
            action="Load", effect=Condition(loaded), duration=2))
        self.assertTrue(isinstance(description.statements[1], Releases))
        self.assertEqual(description.statements[1], Releases(
            action="Load", effect=Condition(~hidden), duration=1))
        self.assertTrue(isinstance(description.statements[2], Causes))
        self.assertEqual(description.statements[2], Causes(
            action="Shoot", effect=Condition(~loaded), duration=1))
        self.assertTrue(isinstance(description.statements[3], Causes))
        self.assertEqual(description.statements[3], Causes(
            action="Shoot",
            effect=Condition(~alive), condition=Condition(~hidden & loaded),
            duration=1))
        self.assertTrue(isinstance(description.statements[4], ImpossibleIf))
        self.assertEqual(description.statements[4], ImpossibleIf(
            action="Shoot", condition=Condition(~loaded)))
