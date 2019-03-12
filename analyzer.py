import json
import glob
import re
import sys
import os
from pprint import pprint

BRAGG_DEPENDENCY = 'bragg-route-invoke'
JSON_EXTENSION = '.json'
SERVICE_DEPENDENCY = ':v0'
BLACKLISTED_DIRS = ["/node_modules/", "/dist/", "/test/"]


def scan_line_with_dep_name(lines: [str], dep_name: {str: str}) -> [str]:
    matches = []

    for line in lines:
        for key, _ in dep_name.items():
            if f"config.{key}" in line:
                matches.append(line)

    return matches


def map_dependencies(path: str) -> {str: str}:
    filtered_dependencies = {}

    with open(path) as json_file:
        data = json.load(json_file)

        for key, value in data['production'].items():
            if SERVICE_DEPENDENCY in value:
                filtered_dependencies[key] = value
        json_file.close()

    return filtered_dependencies


def extract_service_name(path: str) -> str:
    with open(path) as package_json:
        data = json.load(package_json)
        name = data["name"]
        package_json.close()

    return name


def clean_data(dependency_list: [str]) -> [str]:
    cleaned_data = [
        dependency
        .replace('\t', '')
        .replace('\n', '')
        for dependency in dependency_list
    ]

    regex = re.compile(r"\([a-zA-Z\.]{0,}" + re.escape("config") + "[a-zA-z\.\,\'\s\n]{1,}")

    matches = []

    for item in cleaned_data:
        if regex.search(item):
            matches.append(regex.search(item).group())

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
                if re.search(r".{0,}\." + re.escape(key) + "$", alias):
                    resource_path_map[key] = set(list((resource_path_map.get(key) or [])) + [resource_path.strip()])
                else:
                    resource_path_map[key] = set(list((resource_path_map.get(key) or [])))
        except:
            print(f"Not able to parse string {invoke}")

    return dict(map(lambda kv: (deps.get(kv[0]), list(kv[1])), resource_path_map.items()))


def analyze():
    [*_, target] = sys.argv
    path = target

    if os.path.isabs(target) is False:
        path = os.path.join(os.getcwd(), target)

    if os.path.isfile(path):
        raise Exception('This analyzer can only analyze bragg directories')

    mapped_dependencies = {}
    analyzed_lines = []
    service_name = ""

    for deps_file_path in glob.iglob(f"{path}/**/config.json", recursive=True):
        mapped_dependencies = map_dependencies(deps_file_path)

    for package_json_path in glob.iglob("{path}/**/package.json", recursive=True):
        if any(black_listed_dir in package_json_path for black_listed_dir in BLACKLISTED_DIRS):
            continue

        service_name = extract_service_name(package_json_path)

    if len(mapped_dependencies.keys()) == 0:
        print('No bragg dependencies')

        return

    for source_file in glob.iglob(f"{path}/**/*.ts", recursive=True):
        if any(black_listed_dir in source_file for black_listed_dir in BLACKLISTED_DIRS):
            continue

        with open(source_file, 'r') as file:
            if BRAGG_DEPENDENCY is False in file:
                file.close()
                continue
            else:
                analyzed_lines = analyzed_lines + scan_line_with_dep_name(file.readlines(), mapped_dependencies)
                file.close()

    cleaned_data = clean_data(analyzed_lines)
    service_map = map_to_dep_dict(cleaned_data, mapped_dependencies)

    destination_path = os.path.join(os.getcwd(), f"{service_name}.json")

    with open(destination_path, 'w') as destination:
        json.dump(service_map, destination)
        destination.close()

    pprint(service_map)

    return


analyze()
