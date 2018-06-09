from structs.domain_description import DomainDescription

def parse_file(file: str) -> DomainDescription:
    with open(file) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]

    return DomainDescription(lines)
