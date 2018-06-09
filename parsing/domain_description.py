def parse(file: str):
    content = []
    with open(file) as f:
        content = f.readlines()
    content = [x.strip().split(' ') for x in content]
    return content
