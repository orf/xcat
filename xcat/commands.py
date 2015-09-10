import asyncio

import colorama
import logbook
import ipgetter
from .requests.injectors import get_all_injectors
from .executors import xpath1, xpath2, docfunction
from xcat.features.oob_http import OOBDocFeature
from .features.doc import DocFeature
from .features.xpath_2 import XPath2
from .features.entity_injection import EntityInjection
from .xpath import E, N, document_uri, doc
from .output import XMLOutput, JSONOutput
from .requests import detector
from .requests.requester import RequestMaker
from .oob.http import OOBHttpServer

colorama.init()


def get(executor, query, output):
    run_then_return(
        display_results(output, executor, E(query))
    )


def structure(executor, query, output):
    run_then_return(
        display_results(output, executor, E(query), simple=True)
    )


def get_uri(executor, out):
    uri = run_then_return(
        executor.get_string(document_uri(N("/")))
    )
    out.write("URI: {uri}\n".format(uri=uri))


def test(detector, target_parameter, unstable, out):
    if target_parameter == "*":
        params = detector.requests.get_url_parameters()
    else:
        params = [target_parameter]

    for param in params:
        out.write("Testing parameter {param}\n".format(param=param))
        detector.change_parameter(param)

        injectors = run_then_return(get_injectors(
            detector, with_features=True, unstable=unstable
        ))

        if len(injectors) == 0:
            out.write("Could not inject into parameter {param}\n".format(param=param))

        for injector, features in injectors.items():
            out.write("\t{name}\t\t{example}\n".format(name=injector.__class__.__name__, example=injector.example))
            for feature in features:
                out.write("\t\t-{name}\n".format(name=feature.__name__))
            out.write("\n")


def test_injection(ctx):
    detector = ctx.obj["detector"]

    if ctx.obj["target_param"] == "*":
        params = detector.requests.get_url_parameters()
    else:
        params = [ctx.obj["target_param"]]

    for param in params:
        click.echo("Testing parameter {}{}{}:".format(colorama.Fore.RED, param, colorama.Fore.RESET))
        detector = detector.change_parameter(param)

        injectors = run_then_return(get_injectors(detector, with_features=True))

        if len(injectors) == 0:
            click.echo("Could not inject into parameter. Are you sure it is vulnerable?")

        for injector, features in injectors.items():
            injector_example = "{}:\t\t{}".format(injector.__class__.__name__, injector.example) \
                .replace("?", colorama.Fore.GREEN + "?" + colorama.Fore.RESET)
            click.echo(injector_example)

            for feature in features:
                click.echo("\t- {}".format(feature.__name__))


def console(ctx):
    current_node = "/*[1]"
    executor = ctx.obj["executor"]

    @asyncio.coroutine
    def command_attr(node, params):
        attribute_count = yield from executor.count_nodes(node.attributes)
        attributes_result = yield from executor.get_attributes(node, attribute_count)

        if attribute_count == 0:
            click.echo("No attributes found.")
        else:
            for name in attributes_result:
                if not name == "":
                    click.echo("%s = %s" % (name, attributes_result[name]))

    @asyncio.coroutine
    def command_ls(node, params):
        child_node_count_result = yield from executor.count_nodes(node.children)
        click.echo("%i child node found." % child_node_count_result)

        futures = map(asyncio.Task,
                      (executor.get_string(child.name) for child in node.children(child_node_count_result)))
        results = (yield from asyncio.gather(*futures))

        for result in results:
            click.echo(result)

    @asyncio.coroutine
    def command_cd(node, params):
        if len(params) < 1:
            click.echo("You must specify a node to navigate to.")
            return

        selected_node = params[0]

        # We consider anything that starts with a slash is an absolute path
        if selected_node[0] == "/":
            new_node = selected_node
        elif selected_node == "..":
            new_node = "/".join(current_node.split("/")[:-1])
        elif selected_node == ".":
            new_node = current_node
        else:
            new_node = current_node + "/" + selected_node

        if (yield from executor.is_empty_string(E(new_node).name)):
            click.echo("Node does not exists.")
        else:
            return new_node

    @asyncio.coroutine
    def command_content(node, params):
        text_count = yield from executor.count_nodes(node.text)
        click.echo((yield from executor.get_node_text(node, text_count)))

    @asyncio.coroutine
    def command_comment(node, params):
        comment_count = yield from executor.count_nodes(node.comments)
        click.echo("%i comment node found." % comment_count)

        for comment in (yield from executor.get_comments(node, comment_count)):
            click.echo("<!-- %s -->" % comment)

    @asyncio.coroutine
    def command_name(node, params):
        node_name = yield from executor.get_string(E(current_node).name)
        click.echo(node_name)

    commands = {
        "ls": command_ls,
        "attr": command_attr,
        "cd": command_cd,
        "content": command_content,
        "comment": command_comment,
        "name": command_name
    }

    while True:
        command = click.prompt("%s : " % current_node, prompt_suffix="")
        command_part = command.split(" ")
        command_name = command_part[0]
        parameters = command_part[1:]

        if command_name in commands:
            command_execution = commands[command_name](E(current_node), parameters)
            new_node = run_then_return(command_execution)

            if not new_node == None:
                current_node = new_node
        else:
            click.echo("Unknown command")


def file_shell(ctx):
    requester = ctx.obj["requester"]
    click.echo("These are the types of files you can read:")
    if requester.has_feature(EntityInjection):
        click.echo(" * Arbitrary text files that do not contain XML, or files that do and do not contain '-->'")
    if requester.has_feature(DocFeature):
        click.echo(" * Local XML files")
    if requester.has_feature(OOBDocFeature):
        click.echo(" * Valid XML files available over the network")

    # ToDo: Make this more like a shell, with a current directory etc. Make it more usable :)
    click.echo("There are three ways to read files on the file system using XPath:")
    click.echo(" 1. inject: Can read arbitrary text files as long as they do not contain any XML")
    click.echo(" 2. comment: Can read arbitrary text files containing XML snippets, but cannot contain '-->'")
    click.echo(
        " 3. doc: Reads valid XML files - does not support any other file type. Supports remote file URI's (http) and local ones.")
    click.echo("Type doc, inject or comment to switch modes. Defaults to inject")
    click.echo("Type uri to read the URI of the document being queried")
    click.echo(
        "Note: The URI should have a protocol prefix. Bad things may happen if the URI does not exist, and it is best to use absolute paths.")
    click.echo("When using the example application use 'file:' as a prefix, not 'file://'.")

    try:
        entity_injection = ctx.obj["requester"].get_feature(EntityInjection)
    except Exception:
        entity_injection = None

    # ToDo: Make doc injection verify that the files exist
    commands = {
        "doc": lambda p: run_then_return(display_results(XMLOutput(), ctx.obj["executor"], doc(p).add_path("/*[1]"))),
        "inject": lambda p: click.echo(run_then_return(entity_injection.get_file(ctx.obj["requester"], file_path))),
        "comment": lambda p: click.echo(
            run_then_return(entity_injection.get_file(ctx.obj["requester"], file_path, True))),
    }
    numbers = {
        "1": "inject",
        "2": "comment",
        "3": "doc"
    }
    mode = "inject"

    while True:
        file_path = click.prompt(">> ", prompt_suffix="")
        if file_path == "exit":
            ctx.exit()

        if file_path == "uri":
            executor = ctx.obj["executor"]
            uri = run_then_return(
                executor.get_string(document_uri(N("/")))
            )
            click.echo("URI: {}".format(uri))
        elif file_path in commands or file_path in numbers:
            if file_path in numbers:
                file_path = numbers[file_path]
            mode = file_path
            click.echo("Switched to {}".format(mode))
        else:
            try:
                commands[mode](file_path)
            except KeyboardInterrupt:
                click.echo("Command cancelled, CTRL+C again to terminate")
            except Exception as e:
                import traceback
                click.echo("Error reading file. Try another mode: {0}".format(e))


@asyncio.coroutine
def display_results(output, executor, target_node, simple=False, first=True):
    if first:
        output.output_started()

    children = []
    node = yield from executor.retrieve_node(target_node, simple)
    output.output_start_node(node)

    if node.child_count > 0:
        for child in target_node.children(node.child_count):
            children.append((yield from display_results(output, executor, child, simple, first=False)))

    output.output_end_node(node)
    data = node._replace(children=children)

    if first:
        output.output_finished()

    return data


def run_then_return(generator):
    future = asyncio.Task(generator)
    asyncio.get_event_loop().run_until_complete(future)
    return future.result()


@asyncio.coroutine
def get_injectors(detector, with_features=False, unstable=False):
    injectors = yield from detector.detect_injectors(unstable)
    if not with_features:
        return {i: [] for i in injectors}
    # Doesn't work it seems. Shame :(
    # return{injector: (yield from detector.detect_features(injector))
    #        for injector in injectors}
    returner = {}
    for injector in injectors:
        returner[injector] = (yield from detector.detect_features(injector))
    return returner