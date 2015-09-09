"""
XCat.

Usage:
    xcat [--match-method=<method>] [--method=<method>]
         [--true|--false] [--debug] [--ip=<ip> --port=<port>]
         [--limit=<limit>] [--xversion=<ver>]
         [--body=<body>] [--cookies=<cookies>]
         <command> <url> <parameter> <match>

Where command is one of the following:
    get         The default
    test        Test if the parameter is injectable
    file-shell  Open a shell-like interface to read files
    console     Open a shell-like interface to explore the document
    structure   Retrieve the structure of the document but no data

Options:
    -M, --match-method=<method> Method of matching [default: string].
    -m, --method=<method>       HTTP Method to use for requests [default: GET].
    -t, --true                  Indicates match_string is a True response.
    -f, --false                 Indicates match_string is a False response.
    -d. --debug                 Debug requests and responses.
    -i, --ip=<ip>               Public IP to use with OOB connects [default: autodetect].
    -p, --port=<port>           Port to use for OOB connections [default: 80]
    -l, --limit=<limit>         Max number of concurrent connections to the target [default: 20].
    -x, --xversion=<ver>        XCat version to use [default: autodetect].
    -b, --body=<body>           A string that will be sent with the request body.
    -c, --cookies=<cookies>     A string with all cookies to be sent, or a file containing all cookie data.
"""

from xcat import commands
import docopt
import ipgetter
import logging
import sys
from xcat.features import OOBDocFeature
from xcat.oob.http import OOBHttpServer
from xcat.requests import RequestMaker

logger = logging.getLogger("xcat")
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(stream=sys.stderr))


def run():
    arguments = docopt.docopt(__doc__)

    if arguments["--debug"]:
        logger.setLevel(logging.DEBUG)

    url = arguments["<url>"]
    target_parameter = arguments["<parameter>"]
    match_string = arguments["<match>"]
    method = arguments["--method"]
    limit = arguments["--limit"]

    if arguments.get("--true", True):
        checker = lambda r, b: match_string in b
    else:
        checker = lambda r, b: not match_string in b

    listen_port = arguments["--port"]

    if not listen_port.isdigit():
        logger.error("Port is not a digit")
        sys.exit(-1)

    if arguments["--ip"] == "autodetect":
        try:
            listen_ip = ipgetter.IPgetter().get_externalip()
        except Exception:
            logger.error("Could not detect public IP, please explicitly specify")
            sys.exit(1)

        logger.debug("Public IP: %s", listen_ip)
    else:
        listen_ip = arguments["--ip"]

    OOBDocFeature.server = OOBHttpServer(host=listen_ip, port=listen_port)
    request_maker = RequestMaker(url, method, target_parameter if target_parameter != "*" else None,
                                 checker=checker, limit_request=limit)


    try:
        commands.run()
    except Exception as e:
        print("Error: {}".format(e))

        sys.exit(-1)


if __name__ == "__main__":
    run()