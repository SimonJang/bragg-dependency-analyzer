import json
import glob
import re
import sys
import os
from pprint import pprint

# Analyze a bragg project and retrieve the dependencies
BRAGG_DEPENDENCY = 'bragg-route-invoke'
JSON_EXTENSION = '.json'


def scan_line_with_dep_name(lines: [str], dep_name: {str: str}) -> [str]:
    matches = []

    for line in lines:
        for key, _ in dep_name.items():
            if key in line:
                matches.append(line)

    return matches


def map_dependencies(path: str) -> {str: str}:
    with open(path) as json_file:
        data = json.load(json_file)
        return data['production']


def clean_data(dependency_list: [str]) -> [str]:
    cleaned_data = [
        dependency
        .replace('\t', '')
        .replace('\n', '')
        for dependency in dependency_list
    ]

    pprint(cleaned_data)

    regex = re.compile(r'\([a-zA-z\.\,\'\s\n]*\)')

    return list(filter(regex.match, cleaned_data))


def analyze():
    [*_, target] = sys.argv;
    path = target

    if os.path.isabs(target) is False:
        path = os.path.join(os.getcwd(), target)

    if os.path.isfile(path):
        raise Exception('This analyzer can only analyze bragg directories')

    mapped_dependencies = {}
    analyzed_lines = []

    for deps_file_path in glob.iglob('{0}/**/config.json'.format(path), recursive=True):
        print('DEPS FILE LOCATION', deps_file_path)
        mapped_dependencies = map_dependencies(deps_file_path)

    for source_file in glob.iglob('{0}/**/*.ts'.format(path), recursive=True):
        print('SOURCE FILE', source_file)

        with open(source_file, 'r') as file:
            if BRAGG_DEPENDENCY is False in file:
                file.close()
                continue
            else:
                analyzed_lines = analyzed_lines + scan_line_with_dep_name(file.readlines(), mapped_dependencies)
                file.close()

    pprint(mapped_dependencies)
    # pprint(analyzed_lines)
    print('cleaned data')
    pprint(clean_data(analyzed_lines))


analyze()
