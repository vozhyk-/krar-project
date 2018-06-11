import unittest
import sympy
import parsing.query


class QueryTestCase(unittest.TestCase):
    def test_parse_example(self):
        queries = parsing.query.parse_file("../example/queries.txt")
        self.assertEqual(len(queries), 6)