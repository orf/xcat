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
import contextlib
import functools
from typing import List, Tuple
import asyncio

import click

from xcat import algorithms, utils
from xcat.attack import AttackContext, Encoding
from xcat.display import display_xml
from xcat.features import detect_features, Feature
from xcat.injections import detect_injections, Injection, injectors
from xcat.shell import shell_loop


@click.group()
def cli():
    pass


def attack_options(func):
    @cli.command()
    @click.option('-m', '--method', default='GET', show_default=True)
    @click.option('-h', '--headers', required=False, type=utils.HeaderFile())
    @click.option('-b', '--body', required=False, type=click.File('rb'))
    @click.option('-e', '--encode', default=Encoding.URL, type=utils.EnumType(Encoding))
    @click.option('-f', '--fast-mode', is_flag=True, type=bool, default=False, show_default=True)
    @click.option('-c', '--concurrency', type=int, default=10, show_default=True)
    @click.option('-ts', '--true-string', required=False, type=utils.NegatableString(),
                  help="Interpret this string in the response body as being a truthful request. Negate with '!'")
    @click.option('-tc', '--true-code', required=False, type=utils.NegatableInt(),
                  help="Interpret this response code as being a truthful request. Negate with '!'")
    @click.option('--enable', required=False, type=utils.FeatureChoice())
    @click.option('--disable', required=False, type=utils.FeatureChoice())
    @click.option('--oob', required=False,
                  help='IP:port to listen on for OOB attacks. This enables the OOB server.')
    @click.argument('url')
    @click.argument('target_parameter')
    @click.argument('parameters', nargs=-1, type=utils.DictParameters())
    @click.pass_context
    @functools.wraps(func)
    def wrapper(ctx, url, target_parameter, parameters, concurrency, fast_mode, body, headers, method,
                encode, true_string, true_code, enable, disable, oob, **kwargs):
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
            oob_details=oob
        )

        if enable:
            context.features.update({k: True for k in enable})

        if disable:
            context.features.update({k: False for k in disable})

        return func(context, **kwargs)

    return wrapper


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


@attack_options
def shell(attack_context):
    asyncio.run(start_shell(attack_context))


@cli.command()
def ip():
    ip = utils.get_ip()
    if not ip:
        click.echo('Could not find an external IP', err=True)
    else:
        click.echo(ip)
    return


@cli.command()
def injections():
    click.echo(f'Supports {len(injectors)} injections:')
    for injector in injectors:
        click.echo(' - Name: ' + click.style(injector.name, 'bright_green'))
        formatted_example = injector.example.replace('?', click.style('?', 'red'))
        click.echo('   Example: ' + formatted_example)
        click.echo('   Tests:')
        for payload, expected in injector.test_payloads(click.style('?', 'red')):
            res = click.style('passes' if expected else 'fails', 'green' if expected else 'red')
            click.echo(f'   - {payload} = {res}')



async def get_injections(context: AttackContext):
    async with context.start() as ctx:
        return await detect_injections(ctx)


async def get_features(context: AttackContext, injection: Injection):
    async with context.start() as ctx:
        return await detect_features(ctx, injection)


@contextlib.asynccontextmanager
async def setup_context(context: AttackContext) -> AttackContext:
    injections = await get_injections(context)
    if not injections:
        click.echo(click.style('Error: No injections detected', 'red'), err=True)
        exit(1)
    features = await get_features(context, injections[0])
    for feature, available in features:
        if feature.name in context.features:
            # This will have been force enable or disabled via the CLI flags
            continue
        context.features[feature.name] = available
    async with context.start(injections[0]) as ctx:
        if context.features['oob-http']:
            oob_ctx_manager = ctx.start_oob_server
        else:
            oob_ctx_manager = ctx.null_context
        async with oob_ctx_manager() as oob_ctx:
            yield oob_ctx


async def start_attack(context: AttackContext):
    async with setup_context(context) as ctx:
        await display_xml([await algorithms.get_nodes(ctx)])


async def start_shell(context: AttackContext):
    async with setup_context(context) as ctx:
        await shell_loop(ctx)


if __name__ == '__main__':
    cli()
