#!/usr/bin/env python3

import argparse
from structs.query import Query
from engine.inconsistency_checker import InconsistencyChecker
from engine.preprocessor import Preprocessor
from engine.engine import Engine
import parsing.scenario
import parsing.domain_description
import parsing.query


def main(library_file: str, scenario_file: str, query_file: str = None):
    scenario = parsing.scenario.parse_file(scenario_file)
    domain_desc = parsing.domain_description.parse_file(library_file)
    queries = parsing.query.parse_file(query_file)
    engine = Engine()

    if len(queries) == 0:
        print("The library and the scenario are valid.")

    if engine.run(scenario=scenario, domain_desc=domain_desc):
        print('After the engine ran We found', len(engine.models), 'models')
        i = 0
        for model in engine.models:
            print('Final model:', i, '\n', model)
            print('Action history for model', i, 'is:', model.action_history)
            i += 1
        if len(engine.models) != 0:
            for query in queries:
                print('Query:', query, 'was evaluated to:', query.validate(engine.models, scenario))
        else:
            print('Query cannot be evaluated due to lack of models')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library-file', nargs='?', type=str, default='example/lib.adl3',
                        const='example/lib.adl3', help='Path to input ADL3 domain description file')
    parser.add_argument('-s', '--scenario-file', nargs='?', type=str, default='example/scenario.txt',
                        const='example/scenario.txt', help='Path to input ADL3 scenario file')
    parser.add_argument('-q', '--query-file', nargs='?', type=str, default='example/queries.txt', help='Query file to be parsed')
    args = vars(parser.parse_args())

    main(**args)
