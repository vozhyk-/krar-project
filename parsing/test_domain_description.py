import unittest

import parsing.domain_description


class DomainDescriptionParsingTestCase(unittest.TestCase):
    def test_parse_example(self):
        description = parsing.domain_description.parse_file("example/lib.adl3")

        assert len(description) == 4
