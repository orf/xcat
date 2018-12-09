# Attack options

All commands except `ip` take the same arguments. These describe the attack you are making, 
and allows xcat to explore it and work out what features it can use.

At _minimum_ you need to supply:

- A URL to attack (`url`)
- A target parameter which is vulnerable to XPath injection (`target_parameter`)
- A value for this parameter, and optionally others if required (`parameters`)
- A string or a status code that is present in the response if the condition is True (`--true-string` and `--true-code`)

For example, to attack the [example vulnerable application](https://github.com/orf/xcat_app) you would use:

`xcat run http://localhost:4567/ query query=Rogue --true-string=Lawyer` 

This instructs `xcat` that:

- The vulnerable URL is `http://localhost:4567/`
- The vulnerable parameter is `query`
- The parameters to pass to the URL are `query=Rogue`
- The true condition is `Lawyer` being present in the response

## Additional options

There are a number of additional options you can use.

# Detect

