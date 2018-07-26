import unittest
import sympy
import parsing.query
import structs.query
import structs.query
from structs.statements import Causes, Releases, ImpossibleIf
from structs.condition import Condition


class QueryTestCase(unittest.TestCase):
    def test_parse_example(self):
        queries = parsing.query.parse_file("example/queries.txt")
        # self.assertEqual(len(queries), 6)
        assert len(queries) == 8

        # necessary executable load,shoot in 3 (ActionQuery)
        self.assertEqual(queries[0].query_type, structs.query.QueryType.NECESSARY)
        self.assertEqual(queries[0].actions, ["load", "shoot"])
        self.assertEqual(queries[0].duration, 3)

        # possibly executable shoot in 1 (ActionQuery)
        self.assertEqual(queries[1].query_type, structs.query.QueryType.POSSIBLY)
        self.assertEqual(queries[1].actions, ["shoot"])
        self.assertEqual(queries[1].duration, 1)

        # possibly executable shoot in 2 (ActionQuery)
        self.assertEqual(queries[2].query_type, structs.query.QueryType.POSSIBLY)
        self.assertEqual(queries[2].actions, ["shoot"])
        self.assertEqual(queries[2].duration, 2)

        alive, loaded, hidden = sympy.symbols("alive, loaded, hidden")
        # necessary alive & ~loaded at 0 when scenario.txt (ScenarioQuery)
        self.assertEqual(queries[3].query_type, structs.query.QueryType.NECESSARY)
        self.assertEqual(queries[3].condition.formula, alive & ~loaded)
        self.assertEqual(queries[3].time_point, 0)

        # possibly hidden at 2 when scenario.txt (ScenarioQuery)
        self.assertEqual(queries[4].query_type, structs.query.QueryType.POSSIBLY)
        self.assertEqual(queries[4].condition.formula, hidden)
        self.assertEqual(queries[4].time_point, 2)

        # necessary ~hidden at 3 when scenario.txt (ScenarioQuery)
        self.assertEqual(queries[5].query_type, structs.query.QueryType.NECESSARY)
        self.assertEqual(queries[5].condition.formula, ~hidden)
        self.assertEqual(queries[5].time_point, 3)

        # possibly ~loaded & ~alive at 4 when scenario.txt (ScenarioQuery)
        self.assertEqual(queries[6].query_type, structs.query.QueryType.POSSIBLY)
        self.assertEqual(queries[6].condition.formula, ~loaded & ~alive)
        self.assertEqual(queries[6].time_point, 4)

        # necessary ~loaded & ~alive at 4 when scenario.txt (ScenarioQuery)
        self.assertEqual(queries[7].query_type, structs.query.QueryType.NECESSARY)
        self.assertEqual(queries[7].condition.formula, ~loaded & ~alive)
        self.assertEqual(queries[7].time_point, 4)
