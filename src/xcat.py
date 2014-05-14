import asyncio
import click
import colorama
import logbook
import sys
import functools

from lib.features import get_available_features
from lib import requests
from lib.executors import xpath1
from lib.xpath import expression
from lib.output import xml
from lib.requests import detector

colorama.init()


@click.group()
@click.argument("target")
@click.argument("arguments")
@click.argument("target_parameter")
@click.argument("match_string")
@click.option("--method", help="HTTP method to use", default="POST")

@click.option("--true", "detection_method", flag_value="true", default=True, help="match_string indicates a true response")
@click.option("--false", "detection_method", flag_value="false", help="match_string indicates a false response")
@click.option("--error", "detection_method", flag_value="error", help="match_string indicates an error response")

@click.option("--loglevel", type=click.Choice(["debug", "info", "warn", "error"]), default="error")
@click.option("--logfile", type=click.File("wb"), default="-")
@click.pass_context
def xcat(ctx, target, arguments, target_parameter, match_string, method, detection_method, loglevel, logfile):
    null_handler = logbook.NullHandler()
    null_handler.push_application()

    out_handler = logbook.StreamHandler(logfile, level=getattr(logbook, loglevel.upper()))
    out_handler.push_application()

    if detection_method == "true":
        checker = functools.partial(check_true, match_string)# lambda r, b: match_string in b
    else:
        checker = lambda r, b: not match_string in b

    ctx.obj["detector"] = detector.Detector(target, method, arguments, target_parameter, checker=checker)
    ctx.obj["target_param"] = target_parameter


def check_true(st, r, b):
    return st in b


@xcat.command(help="Test parameter for injectability")
@click.pass_context
def test_injection(ctx):
    detector = ctx.obj["detector"]

    click.echo("Testing parameter {}:".format(ctx.obj["target_param"]))

    injectors = run_then_return(detector.detect_injectors())

    if len(injectors) == 0:
        click.echo("Found 0 injectors, are you sure the parameter is vulnerable?")
    else:
        click.echo("Found {} injectors. Testing features...".format(len(injectors)))

        for injector in injectors:
            features = run_then_return(detector.detect_features(injector(detector)))

            injector_example = "{}:\t\t{}".format(injector.__name__, injector.EXAMPLE)\
                .replace("?", colorama.Fore.GREEN + "?" + colorama.Fore.RESET)
            click.echo(injector_example)

            for feature in features:
                click.echo("\t- {}".format(feature.__name__))


@xcat.command(help="Test parameters for features")
@click.pass_context
def test_features(ctx):
    detector = ctx.obj["detector"]



@asyncio.coroutine
def retrieve_node(executor, target_node):
    children = []

    data = yield from executor.retrieve_node(target_node)
    print("Got node: {}".format(data))
    if data.child_count > 0:
        for child in target_node.children(data.child_count):
            children.append((yield from retrieve_node(executor, child)))

    data = data._replace(children=children)

    return data

@click.command()
def run(target):
    loop = asyncio.get_event_loop()
    detect = detector.Detector(target, "POST", "title=Bible", target_parameter="title",
                               checker=lambda r, b: "Book found" in b)
    future = asyncio.Task(detect.detect_injectors())
    loop.run_until_complete(future)

    for cls in future.result():
        example = "{}:\t\t{}".format(cls.__name__, cls.EXAMPLE)\
            .replace("?", colorama.Fore.GREEN + "?" + colorama.Fore.RESET)
        click.echo(example)

    #feature_task = asyncio.Task(get_available_features(requester))
    #loop.run_until_complete(feature_task)
    print(future.result())
    return

    task = asyncio.Task(retrieve_node(xpath1.XPath1Executor(requester), expression.Node("/*[1]")))
    loop.run_until_complete(task)
    print(xml.output_node(task.result()).getvalue())
    print("%s requests sent" % requester.requests_sent)
    loop.close()


def run_then_return(generator):
    future = asyncio.Task(generator)
    asyncio.get_event_loop().run_until_complete(future)
    return future.result()


if __name__ == "__main__":
    xcat(obj={})