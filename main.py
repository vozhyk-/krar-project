#!/usr/bin/env python3

import argparse

from language_structure import LanguageStructure
from scenario import Scenario
from query import Query
from scenario_parser import ScenarioParser


def main(library_file: str, scenario_file: str, query: str = None):
    structure = LanguageStructure(library_file)
    sc_parser = ScenarioParser()
    sc_parser.parse(scenario_file)

    raw_query = query
    if raw_query is None:
        print("The library and the scenario are valid.")
    else:
        query = Query(raw_query)
        result = structure.query(query)
        print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library-file', nargs='?', type=str, default='lib.adl3',
                        const='lib.adl3', help='Path to input ADL3 file')
    parser.add_argument('-s', '--scenario-file', nargs='?', type=str, default='scenario.adl3',
                        const='scenario.adl3', help='Path to input ADL3 scenario file')
    parser.add_argument('-q', '--query', nargs='?', type=str, help='Query string to be executed')
    args = vars(parser.parse_args())

    main(**args)
