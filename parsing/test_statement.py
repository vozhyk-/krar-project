import unittest

import parsing.statement
from structs.statements import ImpossibleAt

class StatementParsingTestCase(unittest.TestCase):
    def test_impossible_if(self):
        statement = parsing.statement.parse("impossible Work at 14")
        assert isinstance(statement, ImpossibleAt)
