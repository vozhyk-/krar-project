import unittest

import parsing.domain_description
from structs.statements import Causes, Releases, ImpossibleIf


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        description = parsing.domain_description.parse_file("example/lib.adl3")

        assert len(description.statements) == 4

        assert isinstance(description.statements[0], Causes)
        assert isinstance(description.statements[1], Releases)
        assert isinstance(description.statements[2], Causes)
        assert isinstance(description.statements[3], ImpossibleIf)
