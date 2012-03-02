print "Loading.."
import clr
clr.AddReferenceToFile("saxon9he.dll")
clr.AddReferenceToFile("saxon9he-api.dll")
clr.AddReference('System.Xml')
import Saxon.Api
import System.Xml
import System.Uri
import argparse
import BaseHTTPServer
import urlparse
import sys
import cgi
import traceback

page = """
<html>
    <body>
        Book Title:<form action='/' method='POST'>
                <input type='text' name='title' size=50 value="%s">
                <input type='submit'>
             </form>
"""
print "Loading..."
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(page % "")
        self.wfile.write("</body></html>")

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        print postvars
        if "title" in postvars:
            _t = postvars["title"][0]
        else:
            _t = ""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(page % cgi.escape(_t, quote=True))

        if _t:
            try:
                _q = '''doc(concat("http://localhost:8080/exist/rest/books/input.xml?_query=",encode-for-uri("/lib/book[title='%s']")))/*[1]/*'''%_t
                print _q
                result = HandleQuery(_q)
                print result
            except Exception,e:
                self.wfile.write("<b>Exception!</b><br/>")
                self.wfile.write(traceback.format_exc().replace("\n","<br/>"))
            else:
                self.wfile.write("<br />")
                if not args.hide_feedback:
                    if result:
                        self.wfile.write("<b>Book found</b>")
                    else:
                        self.wfile.write("<b>Book not found</b>")

        self.wfile.write("</body></html>")
        print "Done..."

def HandleQuery(query):
    qs = compiler.Compile(query).Load()
    qs.ContextItem = node
    return [x for x in qs.GetEnumerator()]
    #return XmlPrime.XPath.Compile(query, settings.NameTable).EvaluateToItem(dyn_settings)

processor = Saxon.Api.Processor()
compiler = processor.NewXPathCompiler()
doc = processor.NewDocumentBuilder()
reader = System.Xml.XmlReader.Create("input.xml")
node = doc.Build(reader)


if "--shell" in sys.argv:
    while True:
        try:
            print HandleQuery(raw_input("Q: "))
        except Exception,e:
            print e


parser = argparse.ArgumentParser()
parser.add_argument("--port", default=80,dest="port",type=int)
parser.add_argument("--nofeedback", dest="hide_feedback", action="store_true")
args = parser.parse_args()
print args

server_addr = ('localhost',args.port)
httpd = BaseHTTPServer.HTTPServer(server_addr,
                                  RequestHandler)
print "Serving on port %s"%args.port
httpd.serve_forever()
