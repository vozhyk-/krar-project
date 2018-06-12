#!/usr/bin/env python3

import argparse
from language_structure import LanguageStructure
from structs.query import Query
from engine.inconsistency_checker import InconsistencyChecker
import parsing.scenario
import parsing.domain_description
import parsing.query


def main(library_file: str, scenario_file: str, query_file: str = None):
    structure = LanguageStructure(library_file)
    scenario = parsing.scenario.parse_file(scenario_file)
    checker = InconsistencyChecker(scenario)
    parsing.domain_description.parse_file(library_file)
    queries = parsing.query.parse_file(query_file)

    if len(queries) == 0 and checker.is_consistent:
        print("The library and the scenario are valid.")
    else:
        print('Queries:', queries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library-file', nargs='?', type=str, default='example/lib.adl3',
                        const='example/lib.adl3', help='Path to input ADL3 domain description file')
    parser.add_argument('-s', '--scenario-file', nargs='?', type=str, default='example/scenario.txt',
                        const='example/scenario.txt', help='Path to input ADL3 scenario file')
    parser.add_argument('-q', '--query-file', nargs='?', type=str, default='example/queries.txt', help='Query file to be parsed')
    args = vars(parser.parse_args())

    main(**args)
