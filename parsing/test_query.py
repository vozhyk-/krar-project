import unittest
import sympy
import os
import parsing.query
import structs.query
from structs.query import *


os.chdir(os.path.dirname(os.path.abspath(__file__)))


class QueryTestCase(unittest.TestCase):
    def test_parse_example(self):
        queries = parsing.query.parse_file("../example/queries.txt")
        # self.assertEqual(len(queries), 6)
        self.assertEqual(6, len(queries))

        # possibly involved hunter
        self.assertEqual(True, isinstance(queries[0], InvolvedQuery))
        self.assertEqual(structs.query.QueryType.POSSIBLY, queries[0].query_type)
        self.assertEqual(queries[0].agent, "hunter")

        # necessary involved turkey
        self.assertEqual(True, isinstance(queries[1], InvolvedQuery))
        self.assertEqual(structs.query.QueryType.NECESSARY, queries[1].query_type)
        self.assertEqual(queries[1].agent, "turkey")

        alive, loaded, hidden = sympy.symbols("alive, loaded, hidden")
        # possibly executable shoot in 2 (ActionQuery)
        self.assertEqual(True, isinstance(queries[2], ConditionQuery))
        self.assertEqual(structs.query.QueryType.NECESSARY, queries[2].query_type)
        self.assertEqual(alive, queries[2].condition.formula)
        self.assertEqual(4, queries[2].time_point)

        # necessary alive & ~loaded at 0 when scenario.txt (ConditionQuery)
        self.assertEqual(True, isinstance(queries[3], ConditionQuery))
        self.assertEqual(structs.query.QueryType.POSSIBLY, queries[3].query_type)
        self.assertEqual(alive, queries[3].condition.formula)
        self.assertEqual(4, queries[3].time_point)

        # possibly hidden at 2 when scenario.txt (ConditionQuery)
        self.assertEqual(True, isinstance(queries[4], ActionQuery))
        self.assertEqual(structs.query.QueryType.NECESSARY, queries[4].query_type)
        self.assertEqual(["escape"], queries[4].action_strings)
        self.assertEqual(2, int(queries[4].time_point))

        # necessary ~hidden at 3 when scenario.txt (ConditionQuery)
        self.assertEqual(True, isinstance(queries[5], ActionQuery))
        self.assertEqual(structs.query.QueryType.POSSIBLY, queries[5].query_type)
        self.assertEqual(["escape"], queries[5].action_strings)
        self.assertEqual(2, int(queries[5].time_point))
