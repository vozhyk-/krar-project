import unittest

from parsing.domain_description_parser import DomainDescriptionParser


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        parser = DomainDescriptionParser()
        description = parser.parse("example/lib.adl3")

        assert len(description) == 4
