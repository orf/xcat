print "Loading.."
import clr
clr.AddReferenceToFile("XQSharp.dll")
clr.AddReferenceToFile("XQSharp.ExtensionMethods.dll")
clr.AddReference('System.Xml')
import XQSharp
import System.Xml
import argparse
import BaseHTTPServer
import cgi
import sys

page = """
<html>
    <body>
        Book Title:<form action='/' method='POST'>
                <input type='text' name='title'>
                <input type='submit'>
             </form>
"""
print "Loading..."
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(page)
        self.wfile.write("</body></html>")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(page)
        length = int(self.headers.getheader('content-length'))
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        print postvars
        if "title" in postvars:
            result = HandleQuery("/bib/book[title='"+ postvars["title"][0] + "']")
            self.wfile.write("<br />")
            if result:
                self.wfile.write("<b>Book found</b>")
            else:
                self.wfile.write("<b>Book not found</b>")

        self.wfile.write("</body></html>")
        print "Done..."

def HandleQuery(query):
    return XQSharp.XPath.Compile(query, settings.NameTable).EvaluateToItem(dyn_settings)

settings = System.Xml.XmlReaderSettings()
settings.NameTable = System.Xml.NameTable()

reader = System.Xml.XmlReader.Create("input.xml", settings)
document = XQSharp.XdmDocument(reader)

contextItem = document.CreateNavigator()
dyn_settings = XQSharp.DynamicContextSettings()
resolver = System.Xml.XmlUrlResolver()
reader_settings = System.Xml.XmlReaderSettings()

reader_settings.NameTable = settings.NameTable
dyn_settings.DocumentSet = XQSharp.DocumentSet(resolver, reader_settings)
dyn_settings.ContextItem = contextItem

if "--shell" in sys.argv:
    while True:
        try:
            print HandleQuery(raw_input("Q: "))
        except Exception,e:
            print e


parser = argparse.ArgumentParser()
parser.add_argument("--port", default=80,dest="port",type=int)
args = parser.parse_args()

server_addr = ('localhost',args.port)
httpd = BaseHTTPServer.HTTPServer(server_addr,
                                  RequestHandler)
print "Serving on port %s"%args.port
httpd.serve_forever()
