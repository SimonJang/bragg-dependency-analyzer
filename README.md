# bragg-dependency-analyzer
Python script to analyze the dependencies in a `bragg` project

# TODO

- Use `package.json` dependencies to check from `bragg-route-invoke` and `typescript`
- Map other AWS dependencies
- Search for method
- Create data structure for graph
- Work with bragg powered SDK

# DONE
- Exclude node modules folder
- Exact search for the string from the `config.json`
- Retrieve the service name from the `package.json`
- Include JS files if it's not a typescript project by checking typescript dependency

# Other projects

[Create graph based on the data from the dependencies analysis](https://github.com/SimonJang/json-to-json-graph)