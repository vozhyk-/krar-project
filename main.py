#!/usr/bin/env python3

import argparse

from language_structure import LanguageStructure
from structs.query import Query
from engine.inconsistency_checker import InconsistencyChecker
import parsing.scenario
import parsing.domain_description


def main(library_file: str, scenario_file: str, query: str = None):
    structure = LanguageStructure(library_file)
    scenario = parsing.scenario.parse_file(scenario_file)
    checker = InconsistencyChecker(scenario)
    parsing.domain_description.parse_file(library_file)
    raw_query = query
    if raw_query is None and checker.is_consistent:
        print("The library and the scenario are valid.")
    else:
        print("The library and the scenario are not valid.")
        query = Query(raw_query)
        result = structure.query(query)
        #print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library-file', nargs='?', type=str, default='example/lib.adl3',
                        const='example/lib.adl3', help='Path to input ADL3 domain description file')
    parser.add_argument('-s', '--scenario-file', nargs='?', type=str, default='example/scenario.txt',
                        const='example/scenario.txt', help='Path to input ADL3 scenario file')
    parser.add_argument('-q', '--query', nargs='?', type=str, help='Query string to be executed')
    args = vars(parser.parse_args())

    main(**args)
