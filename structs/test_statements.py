import unittest

from structs.statements import Causes, Releases
from structs.condition import Condition


class StatementsTestCase(unittest.TestCase):
    def test_causes_condition_defaults_to_true(self):
        self.check_statement_condition_defaults_to_true(Causes)

    def test_releases_condition_defaults_to_true(self):
        self.check_statement_condition_defaults_to_true(Releases)

    def check_statement_condition_defaults_to_true(self, statement_type: type):
        statement = statement_type(
            action="",
            effect=Condition(False),
            duration=2)
        self.assertEqual(statement.condition, True)

    def test_causes_condition_accepts_value(self):
        self.check_statement_condition_accepts_value(Causes)

    def test_releases_condition_accepts_value(self):
        self.check_statement_condition_accepts_value(Releases)

    def check_statement_condition_accepts_value(self, statement_type: type):
        condition = Condition(False)
        statement = statement_type(
            action="",
            effect=Condition(False),
            condition=condition,
            duration=2)
        self.assertEqual(statement.condition, condition)
