XCat
====

|Build Status| |image1| |image2| |image3| |image4|

.. |Build Status| image:: https://travis-ci.org/orf/xcat.svg?branch=master
   :target: https://travis-ci.org/orf/xcat
.. |image1| image:: https://img.shields.io/pypi/v/xcat.svg
   :target: https://pypi.python.org/pypi/xcat
.. |image2| image:: https://img.shields.io/pypi/l/xcat.svg
   :target: https://pypi.python.org/pypi/xcat
.. |image3| image:: https://img.shields.io/pypi/format/xcat.svg
   :target: https://pypi.python.org/pypi/xcat
.. |image4| image:: https://img.shields.io/pypi/pyversions/xcat.svg
   :target: https://pypi.python.org/pypi/xcat

.. raw:: html

   <a target='_blank' rel='nofollow' href='https://app.codesponsor.io/link/hZfyCKcjPR9bn6Z1vLn1WyHZ/orf/xcat'>
     <img alt='Sponsor' width='888' height='68' src='https://app.codesponsor.io/embed/hZfyCKcjPR9bn6Z1vLn1WyHZ/orf/xcat.svg' />
   </a>

XCat is a command line program that aides in the exploitation of blind XPath injection vulnerabilities. It can be used
to retrieve the whole XML document being processed by a vulnerable XPath query, read arbitrary files on the hosts filesystem
and utilize out of bound HTTP requests to make the server send data directly to xcat.

XCat is built to exploit boolean XPath injections (Where only one bit of data can be extracted in one request)
and it requires you to manually identify the exploit first, this does not do that for you. Check out the docs 
at http://xcat.readthedocs.org/ for more info.

Install:

.. code:: console

   pip3 install xcat

**Note:** This requires Python 3.5 and above to run.


.. code-block:: console

   > xcat --help

   XCat.

   Usage:
       xcat <url> <target_parameter> [<parameters>]... (--true-string=<string> | --true-code=<code>) [--method=<method>]
            [--fast] [--oob-ip=<ip> (--oob-port=<port>)] [--stats] [--concurrency=<val>]
            [--features] [--body] [--cookie=<cookie>] [(--shell | --shellcmd=<cmd>)]
       xcat detectip

   Options:
       -s, --shell                 Open the psudo-shell for exploring injections
       -S, --shellcmd=<cmd>        Execute a single shell command.
       -m, --method=<method>       HTTP method to use for requests [default: GET]
       -o, --oob-ip=<ip>           Use this IP for OOB injection attacks
       -p, --oob-port=<port>       Use this port for injection attacks
       -x, --concurrency=<val>     Make this many connections to the target server [default: 10]
       -b, --body                  Send the parameters in the request body as form data. Used with POST requests.
       -c, --cookie=<cookie>       A string that will be sent as the Cookie header
       -f, --fast                  Only fetch the first 15 characters of string values
       -t, --true-string=<string>  Interpret this string in the response body as being a truthful request. Negate with '!'
       -tc, --true-code=<code>     Interpret this status code as being truthful. Negate with '!'
       --stats                     Print statistics at the end of the session



More examples and documentation can be found at http://xcat.readthedocs.org/

Example Application
-------------------

There is a vulnerable Java web application for testing/demoing available here: https://github.com/orf/xcat_app
