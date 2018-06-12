import unittest
import sympy
import parsing.domain_description
from structs.statements import Causes, Releases, ImpossibleIf
from structs.condition import Condition


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        description = parsing.domain_description.parse_file("example/lib.adl3")

        assert len(description.statements) == 4

        alive, loaded = sympy.symbols("alive,loaded")
        self.assertEqual(description.statements[0], Causes(
            action="Load", effect=Condition(loaded), duration=2))
        self.assertEqual(description.statements[1], Releases(
            action="Load", effect=Condition(loaded), duration=1))
        self.assertEqual(description.statements[2], Causes(
            action="Shoot", effect=Condition(~loaded & ~alive), duration=1))
        self.assertEqual(description.statements[3], ImpossibleIf(
            action="Shoot", condition=Condition(~loaded)))
