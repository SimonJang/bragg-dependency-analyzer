import json
import re
import sys
import os
from pprint import pprint

# Analyze a bragg project and retrieve the dependencies
BRAGG_DEPENDENCY = 'bragg-route-invoke'
JSON_EXTENSION = '.json'


def discover_import_name(line: str) -> str:
    if BRAGG_DEPENDENCY is False in line:
        return
    [_, __, ___, alias, *_] = line.split(' ')
    print('Alias', alias)
    return alias


def scan_line_with_alias(line: str, alias: str) -> (str, str, str):
    if alias not in line:
        return None
    statement = re.search('invoke.[a-z]{3,4}\([a-zA-z\.\,\'\s]*\)', line)
    print('regex result', statement)
    return


def scan_line_with_dep_name(line: str, dep_name: str) -> (str, str, str):
    if dep_name not in line:
        return
    print(line)


def map_dependencies(path: str) -> {str: str}:
    with open(path) as json_file:
        data = json.load(json_file)
        return data['production']


def analyze():
    print(sys.argv)
    # Target dir
    [*_, target] = sys.argv;

    print(target)
    path = target
    if os.path.isabs(target) is False:
        path = os.path.join(os.getcwd(), target)

    if os.path.isfile(path):
        if JSON_EXTENSION in os.path.basename(path):
            dependencyMap = map_dependencies(path)

            with open(path, 'r') as file:
                for line in file:
                    for key, value in dependencyMap:
                        scan_line_with_dep_name(line, key)
        else:
            # check bragg dependency
            with open(path, 'r') as file:
                if BRAGG_DEPENDENCY is False in file.read():
                    print('No dependency discovered in file {0}'.format(path))
                    return
                else:
                    print('Bragg dependency detected in file {0}'.format(path))
                    print('Scanning file for dependency')

                    deps = []
                    alias = None

                    for line in file:
                        result = discover_import_name(line)

                        if result is not None:
                            alias = result
                            break

                    for line in file:
                        scan_line_with_alias(line, alias)

    else:
        print('{0} is a directory. Scanning...'.format(path))


analyze()

