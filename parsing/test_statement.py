import unittest

import parsing.statement
from structs.statements import ImpossibleAt, ImpossibleIf

class StatementParsingTestCase(unittest.TestCase):
    def test_impossible_at(self):
        statement = parsing.statement.parse("impossible Work at 14")
        self.assertEqual(statement, ImpossibleAt(action="Work", time=14))

    def test_impossible_if(self):
        statement = parsing.statement.parse("impossible Work if sick | dead")
        expected_condition = parsing.condition.parse("sick | dead")
        self.assertEqual(statement,
            ImpossibleIf(action="Work", condition=expected_condition))
