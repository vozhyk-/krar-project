class Fluent:
    def __init__(self, name: str = None, value: bool = None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name + " is " + str(self.value)

    def __eq__(self, other):
        if isinstance(other, Fluent):
            return self.name == other.name and self.value == other.value
        return False
