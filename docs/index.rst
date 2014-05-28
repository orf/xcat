XCat user guide
===============

XCat is a command line program that aides in the exploitation of blind XPath injection vulnerabilities. It can be used
to retrieve the whole XML document being processed by a vulnerable XPath query, read arbitrary files on the hosts filesystem
and utilize out of bound HTTP requests to make the server send data directly to xcat.

XCat is built to exploit boolean XPath injections (Where only one bit of data can be extracted in one request)
and it requires you to manually identify the exploit first, this does not do that for you.

.. toctree::
    :maxdepth: 2

    about

