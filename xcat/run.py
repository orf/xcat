"""
XCat.

Usage:
    xcat <url> <parameter>
    xcat get-uri <url> <parameter>
    xcat test-injection <url> <parameter>
    xcat file-shell <url> <parameter>
    xcat console <url> <parameter>
    xcat structure <url> <parameter>
    xcat retrieve <urL> <parameter> --query='/*[1]'

Options:
    --match=<text>, -m <text>   String to match against
    --method=<method>           HTTP Method to use for requests [default: GET].
    --true                      Indicates match_string is a True response.
    --false                     Indicates match_string is a False response.
    --debug                     Debug requests and responses.
    --public-ip=<ip>            Public IP to use with OOB connects [default: autodetect].
    --limit=<limit>             Max number of concurrent connections to the target [default: 20].
    --xversion=<ver>            XCat version to use [default: autodetect].
    --body=<body_data>          A string that will be sent with the request body.
    --cookies=<cookies>         A string with all cookies to be sent, or a file containing all cookie data.
"""

from xcat import commands
import docopt


def run():
    arguments = docopt.docopt(__doc__)

    try:
        commands.run()
    except Exception as e:
        print("Error: {}".format(e))
        import sys

        sys.exit(-1)
