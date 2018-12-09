XPath supports a surprising feature set that enables reading environment variables, files, directories and even network 
resources. Rather than add individual subcommands to xcat for each of these they are available under a single `shell` 
command that lets you quickly explore and evaluate arbitrary expressions.

It supports interactive help via auto-completions, history and command suggestions.

## Demo

This demo shows the shell in action. Through it I list the current working directory using `ls`, then retrieve 
the Dockerfile using `cat`. I also list the environment variables using `env`

<script id="asciicast-216044" src="https://asciinema.org/a/216044.js" async></script>

## Commands

A full list of commands and their argiuments can be found by running `help` in the shell. At the time of writing
the output is:

```shell
XCat$ help
Available commands:
env: Read environment variables
pwd: Get current working directory
get: [expression] - Fetch a specific node by xpath expression
get-string: [expression] - Fetch a specific string by xpath expression
time: Get the current date+time of the server
cat: [path] - Read a file or directory
toggle: Toggle features on or off
resolve: [path] - Resolve a file name to an absolute URI
find: [name] - Find a file by name in parent directories
expect-data: Add an entry to the OOB server to expect some data
expect-entity-injection: [file_path] - Add an entry to the OOB server to expect a SYSTEM entity injection
get-oob-data: [identifier] - Get OOB data from an identifier
exit: Quit the shell
help: Get help
```
