XPath supports a surprising feature set that enables reading environment variables, files, directories and even network 
resources. Rather than add individual subcommands to xcat for each of these they are available under a single `shell` 
command that lets you quickly explore and evaluate arbitrary expressions.

## Demo

This demo shows the shell in action. Through it I list the current working directory using `ls`, then retrieve 
the Dockerfile using `cat`. I also list the environment variables using `env`

<script id="asciicast-216044" src="https://asciinema.org/a/216044.js" async></script>
