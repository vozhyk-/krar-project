#!/usr/bin/env python3
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library-file', nargs='?', type=str, default='lib.adl3',
                        const='lib.adl3', help='Path to input ADL3 file')
    parser.add_argument('-s', '--scenario-file', nargs='?', type=str, default='scenario.adl3',
                        const='scenario.adl3', help='Path to input ADL3 scenario file')
    parser.add_argument('-q', '--query', nargs='?', type=str, help='Query string to be executed')
    program_args = vars(parser.parse_args())
    print('Program arguments:', program_args)
