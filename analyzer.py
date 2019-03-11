import json
import glob
import re
import sys
import os
from pprint import pprint

BRAGG_DEPENDENCY = 'bragg-route-invoke'
JSON_EXTENSION = '.json'
SERVICE_DEPENDENCY = ':v0'


def scan_line_with_dep_name(lines: [str], dep_name: {str: str}) -> [str]:
    matches = []

    for line in lines:
        for key, _ in dep_name.items():
            if key in line:
                matches.append(line)

    return matches


def map_dependencies(path: str) -> {str: str}:
    filtered_dependencies = {}

    with open(path) as json_file:
        data = json.load(json_file)

        for key, value in data['production'].items():
            if SERVICE_DEPENDENCY in value:
                filtered_dependencies[key] = value
    
    print(filtered_dependencies)

    return filtered_dependencies


def clean_data(dependency_list: [str]) -> [str]:
    cleaned_data = [
        dependency
        .replace('\t', '')
        .replace('\n', '')
        for dependency in dependency_list
    ]

    pprint(cleaned_data)

    regex = re.compile(r'\([a-zA-z\.\,\'\s\n]{1,}\)')

    matches = []

    for item in cleaned_data:
        if regex.search(item):
            matches.append(regex.search(item).group())

    pprint(matches)

    return [
        line
        .replace('(', '')
        .replace(')', '')
        .replace('\'', '')
        for line in matches
    ]


def map_to_dep_dict(invokes: [str], deps: {str: str}) -> {str: str}:
    resource_path_map = {}
    for invoke in invokes:
        try:
            [alias, resource_path, *_] = invoke.split(',')

            for key in deps.keys():
                if key in alias:
                    resource_path_map[key] = (resource_path_map.get(key) or []) + [resource_path]
        except:
            print('Not able to parse string {0}'.format(invoke))

    return resource_path_map


def analyze():
    [*_, target] = sys.argv
    path = target

    if os.path.isabs(target) is False:
        path = os.path.join(os.getcwd(), target)

    if os.path.isfile(path):
        raise Exception('This analyzer can only analyze bragg directories')

    mapped_dependencies = {}
    analyzed_lines = []

    for deps_file_path in glob.iglob('{0}/**/config.json'.format(path), recursive=True):
        mapped_dependencies = map_dependencies(deps_file_path)

    if len(mapped_dependencies.keys()) == 0:
        print('No bragg dependencies')

        return

    for source_file in glob.iglob('{0}/**/*.ts'.format(path), recursive=True):
        with open(source_file, 'r') as file:
            if BRAGG_DEPENDENCY is False in file:
                file.close()
                continue
            else:
                analyzed_lines = analyzed_lines + scan_line_with_dep_name(file.readlines(), mapped_dependencies)
                file.close()

    pprint(analyzed_lines)

    cleaned_data = clean_data(analyzed_lines)
    service_map = map_to_dep_dict(cleaned_data, mapped_dependencies)

    destination_path = os.path.join(os.getcwd(), 'analysis-result.json')
    with open(destination_path, 'w') as destination:
        json.dump(service_map, destination)

    pprint(service_map)

    return


analyze()
