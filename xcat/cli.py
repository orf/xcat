"""
XCat.

Usage:
    xcat <url> <target_parameter> [<parameters>]... (--true-string=<string> | --true-code=<code>) [--method=<method>]
         [--fast] [--oob-ip=<ip> (--oob-port=<port>)] [--stats] [--concurrency=<val>]
         [--features] [--body] [--cookie=<cookie>] [(--shell | --shellcmd=<cmd>)]
    xcat detectip

Options:
    -o, --oob-ip=<ip>           Use this IP for OOB injection attacks
    -p, --oob-port=<port>       Use this port for injection attacks
    --stats                     Print statistics at the end of the session
"""
import functools
from typing import Iterable, List, Tuple

import click
import asyncio
import time

import aiohttp

from xcat.algorithms import get_nodes
from xcat.attack import AttackContext, Encoding
from xcat.display import display_xml
from xcat.features import detect_features, Feature
from xcat.injections import detect_injections, Injection
from xcat.shell import run_shell, run_shell_command
from xcat import utils


@click.group()
def cli():
    pass


def attack_options(func):
    @cli.command()
    @click.option('-m', '--method', default='GET', show_default=True)
    @click.option('-h', '--headers', required=False, type=utils.HeaderFile())
    @click.option('-b', '--body', required=False, type=click.File('rb'))
    @click.option('-e', '--encode', default=Encoding.URL, type=utils.EnumType(Encoding))
    @click.option('-f', '--fast-mode', type=bool, default=False, show_default=True)
    @click.option('-c', '--concurrency', type=int, default=10, show_default=True)
    @click.option('-ts', '--true-string', required=False, type=utils.NegatableString(),
                  help="Interpret this string in the response body as being a truthful request. Negate with '!'")
    @click.option('-tc', '--true-code', required=False, type=utils.NegatableInt(),
                  help="Interpret this response code as being a truthful request. Negate with '!'")
    @click.argument('url')
    @click.argument('target_parameter')
    @click.argument('parameters', nargs=-1, type=utils.DictParameters())
    @click.pass_context
    @functools.wraps(func)
    def wrapper(ctx, url, target_parameter, parameters, concurrency, fast_mode, body, headers, method,
                encode, true_string, true_code):
        if body and encode != 'url':
            ctx.fail('Can only use --body with url encoding')

        if not true_code and not true_string:
            ctx.fail('--true-code or --true-string is required')

        match_function = utils.make_match_function(true_code, true_string)
        parameters = dict(parameters)

        if target_parameter not in parameters:
            ctx.fail(f'target parameter {target_parameter} is not in the given list of parameters')

        body_bytes = None
        if body:
            body_bytes = body.read()

        context = AttackContext(
            url=url,
            method=method,
            target_parameter=target_parameter,
            parameters=parameters,
            match_function=match_function,
            concurrency=concurrency,
            fast_mode=fast_mode,
            body=body_bytes,
            headers=headers,
            encoding=encode,
        )
        return func(context)


@attack_options
def detect(attack_context):
    payloads: List[Injection] = asyncio.run(get_injections(attack_context))

    if not payloads:
        click.echo(click.style('Error: No injections detected', 'red'), err=True)
        exit(1)

    for payload in payloads:
        click.echo(click.style(payload.name, 'green'))
        click.echo(' - Example: ' + click.style(payload.example, 'yellow'))

    features: List[Tuple[Feature, bool]] = asyncio.run(get_features(attack_context, payloads[0]))
    click.echo('Detected features:')
    for feature, available in features:
        click.echo(' - ' + click.style(feature.name, 'blue') + ': ', nl=False)
        click.echo(click.style(str(available), 'green' if available else 'red'))


@attack_options
def run(attack_context):
    asyncio.run(start_attack(attack_context))


@cli.command()
def get_ip():
    ip = utils.get_ip()
    if not ip:
        click.echo('Could not find an external IP', err=True)
    else:
        click.echo(ip)
    return


async def get_injections(context: AttackContext):
    async with context.start() as ctx:
        return await detect_injections(ctx)


async def get_features(context: AttackContext, injection: Injection):
    async with context.start() as ctx:
        return await detect_features(ctx, injection)


async def start_attack(context: AttackContext):
    injections = await get_injections(context)
    if not injections:
        click.echo(click.style('Error: No injections detected', 'red'), err=True)
        exit(1)
    features = await get_features(context, injections[0])
    for feature, available in features:
        context.features[feature.name] = available
    async with context.start(injections[0]) as ctx:
        await display_xml([await get_nodes(ctx)])


async def start_action(url, target_parameter, parameters, match_function, oob_ip, oob_port,
                       shell, shell_cmd, fast, stats, concurrency, only_features, body, cookie, method):
    async with aiohttp.ClientSession() as session:

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
                print('Total Time: {time} seconds'.format(time=round(t2 - t1)))
            print('Total Requests: {requester.total_requests}'.format(requester=requester))
        finally:
            await requester.stop_oob_server()

        if stats:
            print('Stats:')
            for name, counter in requester.counters.items():
                print('{name}:'.format(name=name))
                for name, value in counter.most_common(10):
                    print(' - {name} {value}'.format(name=name, value=value))


if __name__ == '__main__':
    cli()
