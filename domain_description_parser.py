class DomainDescriptionParser:

    def __init__(self):
        pass

    def parse(self, file: str):
        content = []
        with open(file) as f:
            content = f.readlines()
        content = [x.strip().split(' ') for x in content]
        print('Domain descriptions:', content)
