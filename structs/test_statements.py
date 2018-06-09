import unittest

from structs.statements import Causes
from structs.condition import Condition


class StatementsTestCase(unittest.TestCase):
    def test_causes_condition_defaults_to_true(self):
        statement = Causes(action="", effect=Condition(False), duration=2)
        self.assertEqual(statement.condition, True)

    def test_causes_condition_accepts_value(self):
        condition = Condition(False)
        statement = Causes(
            action="",
            effect=Condition(False),
            condition=condition,
            duration=2)
        self.assertEqual(statement.condition, condition)
