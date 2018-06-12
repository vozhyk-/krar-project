from structs.domain_description import DomainDescription
import parsing.statement


def parse_file(file: str) -> DomainDescription:
    with open(file) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    statements = [parsing.statement.parse(x) for x in lines]

    return DomainDescription(statements)
