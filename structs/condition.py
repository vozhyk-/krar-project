import sympy
from sympy.logic import boolalg

class Condition:
    def __init__(self, formula: boolalg.Boolean):
        self.formula = formula
