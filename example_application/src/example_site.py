import sys
import os
if "__file__" in locals():
    sys.path.append(os.path.join(os.path.dirname(__file__), "saxon", "saxon9he.jar"))
else:
    sys.path.append(os.path.join("saxon", "saxon9he.jar"))

if not os.getcwd() in sys.path:
    sys.path.append(os.getcwd()) # in PyCharm this fixes import errors

from javax.xml.xpath import *
from net.sf.saxon.s9api import *
from org.xml.sax import InputSource
from javax.xml.transform.sax import SAXSource
from java.lang import System
from net.sf.saxon.xpath import *

from bottle import route, run, request, error, app

xpf = XPathFactoryImpl()
xpe = xpf.newXPath()
System.err.println("Loaded XPath Provider " + xpe.getClass().getName())

input_s = InputSource("input.xml")
sax_source = SAXSource(input_s)
doc = xpe.setSource(sax_source)

template = """
    <html>
        <body>
            Search Books:
            <form action='/' method='GET'>
                <input type='text' name='title' size=50 value="%s">
                <select name="type">
                    <option value="*">All</option>
                    <option value="books">Books</option>
                    <option value="videos">Videos</option>
                </select>
                <select name="rent_days">
                    <option value="*">Any</option>
                    <option value="5">5 Days</option>
                    <option value="10">10 Days</option>
                </select>
                <input type='submit'>
             </form>
             <br/>
            %s
        </body>
    </html>
    """

@route("/favicon.ico")
def fav():
    return ""

@route('/')
def index():
    try:
        return _index()
    except Exception, e:
        return "Error"

def _index():
    query = request.query.get("title", "")
    search_type = request.query.get("type", "*")
    rent_days = request.query.get("rent_days", "*")
    results = search_library(query, search_type, rent_days)

    results_html = "<strong>%s results found:</strong><br/><br/>" % len(results)

    results_html += "<hr/>".join(
        ("<strong>%s</strong><br/>" % result["title"])
        + "<br/>".join(
            "%s: %s" % (k.replace("_", " "), v) for k, v in result.items() if k != "title"
        )
        for result in results
    )

    return template % (query if query != "*" else "", results_html)


def search_library(query, type="*", rent_days="*"):
    query = ("contains(title/text(), '%s')" % query) if query != "" \
        else "true()"

    query = "%s and rent_days=%s" % (query, rent_days)

    query = "//library/rentals/%s/*[%s]" % (type, query)
    return execute(query)


def getChildren(node):
    returner = []
    axis_iterator = node.iterateAxis(Axis.getAxisNumber(Axis.CHILD))

    while True:
        child = axis_iterator.current()
        if child is not None:
            if child.displayName != "":
                returner.append(child)

        if not axis_iterator.moveNext():
            break

    return returner


def node_to_object(node):
    returner = {}
    for child in getChildren(node):
        if child is None:
            continue

        if child.displayName:
            returner[child.displayName] = child.getStringValue()

    return returner


def execute(query):
    print "Executing: %s" % query
    expression = xpe.compile(query)
    results = expression.evaluate(doc, XPathConstants.NODESET)
    returner = []

    for result in results:
        if result.displayName not in ("book", "video"):
            continue

        returned_result = {
            "type": result.displayName
        }
        returned_result.update(node_to_object(result))
        returner.append(returned_result)
    return returner


if "--shell" in sys.argv:
    while True:
        r = raw_input(">> ")
        try:
            expression = xpe.compile(r)
            results = expression.evaluate(doc, XPathConstants.NODESET)
            print results
            if results:
                print node_to_object(results[0])
        except BaseException, e:
            print "Ex: %s" % e
        except:
            print "Exception!"
            import traceback
            traceback.print_exc()
    sys.exit()

run(host="0.0.0.0", port=8080, debug=False)