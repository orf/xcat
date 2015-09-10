"""
XCat.

Usage:
    xcat [--match-method=<method>] [--method=<method>]
         [--true|--false] [--debug] [--ip=<ip> --port=<port>]
         [--limit=<limit>] [--xversion=<ver>] [--unstable]
         [--body=<body>] [--cookies=<cookies>]
         <command> <url> <parameter> <match>

Where command is one of the following:
    get         The default
    test        Test if the parameter is injectable
    uri         Get the location of the document on the filesystem
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
    -x, --xversion=<ver>        XCat version to use [default: auto].
    -b, --body=<body>           A string that will be sent with the request body.
    -c, --cookies=<cookies>     A string with all cookies to be sent, or a file containing all cookie data.
    -u, --unstable              Ensure responses are stable before executing
"""

import logging
import sys

from xcat import commands
import docopt
import ipgetter
from xcat.executors.docfunction import DocFunctionExecutor
from xcat.executors.xpath1 import XPath1Executor
from xcat.executors.xpath2 import XPath2Executor
from xcat.features import OOBDocFeature, XPath2
from xcat.oob.http import OOBHttpServer
from xcat.requests import RequestMaker, detector
from xcat.commands import run_then_return, get_injectors
from xcat.output import XMLOutput

logger = logging.getLogger("xcat")
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(stream=sys.stderr))


def run():
    arguments = docopt.docopt(__doc__)

    if arguments["--debug"]:
        logger.setLevel(logging.DEBUG)

    command = arguments["<command>"].lower()
    url = arguments["<url>"]
    target_parameter = arguments["<parameter>"]
    match_string = arguments["<match>"]
    method = arguments["--method"]
    limit = arguments["--limit"]
    listen_port = arguments["--port"]
    listen_ip = arguments["--ip"]
    unstable = arguments["--unstable"]
    xversion = arguments["--xversion"]

    allowed_commands = {"get", "test", "uri", "file-shell", "console", "structure"}
    if command not in allowed_commands:
        logger.error("Unknown command {cmd}. Allowed: {allowed}".format(
            cmd=command,
            allowed=" ".join(allowed_commands)
        ))
        sys.exit(-1)

    if not arguments["--true"] and not arguments["--false"]:
        arguments["--true"] = True

    if arguments["--true"]:
        checker = lambda r, b: match_string in b
    else:
        checker = lambda r, b: match_string not in b

    # Validate the inputs

    try:
        listen_port = int(listen_port)
    except ValueError:
        logger.error("Port is not a number")
        sys.exit(1)

    try:
        limit = int(limit)
    except ValueError:
        logger.error("Limit is not a number")
        sys.exit(1)

    if xversion not in {"auto", "1", "2"}:
        logger.error("Invalid --xversion flag. Please choose 'auto', '1' or '2'")
        sys.exit(1)

    if listen_ip == "autodetect":
        try:
            listen_ip = ipgetter.IPgetter().get_externalip()
        except Exception:
            logger.error("Could not detect public IP, please explicitly specify")
            sys.exit(1)

        logger.debug("Public IP: %s", listen_ip)

    OOBDocFeature.server = OOBHttpServer(host=listen_ip, port=listen_port)
    request_maker = RequestMaker(url, method, target_parameter if target_parameter != "*" else None,
                                 checker=checker, limit_request=limit)
    feature_detector = detector.Detector(checker, request_maker)

    if command == "test":
        commands.test(feature_detector, target_parameter, unstable, sys.stdout)
        sys.exit(0)

    injectors = run_then_return(get_injectors(feature_detector, unstable=unstable,
                                              with_features=False))

    injector = list(injectors.keys())[0]  # Hack: todo properly handle >1 injector
    features = run_then_return(feature_detector.detect_features(injector))

    if XPath2 not in features and xversion == "2":
        logger.error("XPath version specified as 2 but could not detect XPath 2 support")
        sys.exit(1)

    executor_cls = XPath1Executor

    if xversion in {"auto", "2"} and XPath2 in features:
        executor_cls = XPath2Executor

    if OOBDocFeature in features:
        executor_cls = DocFunctionExecutor

    requester = feature_detector.get_requester(injector, features=features)
    executor = executor_cls(requester)

    if command == "get":
        commands.get(executor, "/*[1]", XMLOutput(sys.stdout))
    elif command == "file-shell":
        commands.file_shell(requester, executor)
    elif command == "console":
        commands.console(executor)
    elif command == "structure":
        commands.structure(executor, "/*[1]", XMLOutput(sys.stdout))
    elif command == "uri":
        commands.get_uri(executor, sys.stdout)
    else:
        logger.error("Unknown command {command}".format(command=command))
        sys.exit(1)


if __name__ == "__main__":
    run()
