class Fluent:
    def __init__(self, name: str = None, value: bool = None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name + " is " + str(self.value)
