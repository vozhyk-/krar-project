#!/usr/bin/env python3

import argparse
from language_structure import LanguageStructure
from structs.query import Query
from engine.inconsistency_checker import InconsistencyChecker
from engine.preprocessor import Preprocessor
from engine.engine import Engine
import parsing.scenario
import parsing.domain_description
import parsing.query


def main(library_file: str, scenario_file: str, query_file: str = None):
    structure = LanguageStructure(library_file)
    scenario = parsing.scenario.parse_file(scenario_file)
    domain_desc = parsing.domain_description.parse_file(library_file)
    queries = parsing.query.parse_file(query_file)
    prec = Preprocessor()
    unique_domain_desc, unique_scenario = prec.remove_duplicates(domain_desc, scenario)
    # After pre-processing the domain desc and scenario, pass it to the inconsistency_checker
    inconsistency_checker = InconsistencyChecker(unique_domain_desc, unique_scenario)

    if len(queries) == 0:
        print("The library and the scenario are valid.")
    elif inconsistency_checker.is_consistent:
        # Inconsistency checker verified the scenario and domain description, so now we can create our models
        engine = Engine(inconsistency_checker)
        print('After the engine ran We found', len(engine.models), 'model(s):\n', engine.models)
        i = 0
        for model in engine.models:
            print('Final model:', i, '\n', model)
            i += 1
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
