import unittest
import sympy
import parsing.domain_description
from structs.statements import Causes, Releases, ImpossibleIf
from structs.condition import Condition


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        description = parsing.domain_description.parse_file("example/lib.adl3")

        self.assertEqual(len(description.statements), 5)

        alive, loaded, hidden = sympy.symbols("alive,loaded,hidden")
        self.assertEqual(description.statements[0], Causes(
            action="Load", effect=Condition(loaded), duration=2))
        self.assertEqual(description.statements[1], Releases(
            action="Load", effect=Condition(hidden), duration=1))
        self.assertEqual(description.statements[2], Causes(
            action="Shoot", effect=Condition(~loaded), duration=1))
        self.assertEqual(description.statements[3], Causes(
            action="Shoot",
            effect=Condition(~alive), condition=Condition(~hidden),
            duration=1))
        self.assertEqual(description.statements[4], ImpossibleIf(
            action="Shoot", condition=Condition(~loaded)))
