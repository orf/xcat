import pathlib
import os
import time
import sys

from flask import Flask, request, render_template, Response
from sarge import run, Capture
from lxml import etree

app = Flask(__name__)

saxon_jar = pathlib.Path("saxon") / "saxon9he.jar"
library = pathlib.Path("library.xml")

XPATH_1 = "-x1" in sys.argv


@app.route("/")
def index():
    orig_title_query = request.args.get("title", "")
    search_type = request.args.get("type", "*")
    rent_days = request.args.get("rent_days", "*")

    title_query = "contains(title/text(), '{}') ".format(orig_title_query) \
        if orig_title_query else "true()"

    xpath_filter = "{title_query} and rent_days={rent_days}" \
        .format(title_query=title_query, rent_days=rent_days)

    xpath_query = "/*/rentals/{type}/*[{filter}]".format(type=search_type,
                                                         filter=xpath_filter)

    if XPATH_1:
        results, run_time = run_xpath1_query(xpath_query)
    else:
        results, run_time, error = run_xpath2_query(xpath_query)
        if error:
            print(error.decode())

    response = Response(render_template("index.jinja2", results=results, query=orig_title_query))
    response.headers["X-java-time"] = run_time
    response.headers["X-query"] = xpath_query
    print("[{time:1.4f}] {cmd}".format(time=run_time, cmd=xpath_query))
    return response


def run_xpath1_query(query):
    t1 = time.time()
    with open("library.xml", "rb") as fd:
        tree = etree.parse(fd)
    try:
        results = tree.xpath(query)
        return [
            parse_item(result) for result in results
            ], time.time()-t1
    except Exception:
        return []


def run_xpath2_query(query):
    """
    This executes an xpath query against library.xml. It's horrible and relies on calling an external .jar file,
    which makes it very expensive (0.4s per query). Oh well.
    """

    library_arg = "-s:{library} ".format(library=library)
    args = ["java", "-Xms30m", "-cp", str(saxon_jar), "net.sf.saxon.Query", library_arg, "-", "-wrap", "-ext:off"]

    start = time.time()
    p = run(args, stdout=Capture(), stderr=Capture(), cwd=os.getcwd(), input=query)
    output = p.stdout.read()
    error = p.stderr.read()

    try:
        tree = etree.fromstring(output)
        returner = [
            parse_item(result.find("./*")) for result in tree.getchildren()
            ]
    except Exception:
        returner = []

    end = time.time()
    return returner, end - start, error


def parse_item(result):
    children = result.getchildren()
    return {
        child.tag: child.text for child in children
        }


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
