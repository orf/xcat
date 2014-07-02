
import org.xml.sax.Attributes;
import org.xml.sax.ContentHandler;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;

import java.io.PrintStream;


public class ExampleContentHandler implements ContentHandler {

    private PrintStream printStream = System.out;

    public void setPrintStream(PrintStream stream) {
        printStream = stream;
    }

    public PrintStream getPrintStream() {
        return printStream;
    }

    public void setDocumentLocator(Locator locator) {
        printStream.println("setDocumentLocator");
    }

    public void startDocument() throws SAXException {
        printStream.println("startDocument");
    }

    public void endDocument() throws SAXException {
        printStream.println("endDocument");
    }

    public void startPrefixMapping(String prefix, String uri)
            throws SAXException {
        printStream.println("startPrefixMapping: " + prefix + ", " + uri);
    }

    public void endPrefixMapping(String prefix) throws SAXException {
        printStream.println("endPrefixMapping: " + prefix);
    }

    public void startElement(
            String namespaceURI, String localName, String qName, Attributes atts)
                throws SAXException {

        printStream.print("startElement: " + namespaceURI + ", "
                         + localName + ", " + qName);

        int n = atts.getLength();

        for (int i = 0; i < n; i++) {
            printStream.print(", " + atts.getQName(i) + "='" + atts.getValue(i) + "'");
        }

        printStream.println("");
    }

    public void endElement(
            String namespaceURI, String localName, String qName)
                throws SAXException {
        printStream.println("endElement: " + namespaceURI + ", "
                           + localName + ", " + qName);
    }

    public void characters(char ch[], int start, int length)
            throws SAXException {

        String s = new String(ch, start, (length > 30)
                                         ? 30
                                         : length);

        if (length > 30) {
            printStream.println("characters: \"" + s + "\"...");
        } else {
            printStream.println("characters: \"" + s + "\"");
        }
    }

    public void ignorableWhitespace(char ch[], int start, int length)
            throws SAXException {
        printStream.println("ignorableWhitespace");
    }

    public void processingInstruction(String target, String data)
            throws SAXException {
        printStream.println("processingInstruction: " + target + ", "
                           + data);
    }

    public void skippedEntity(String name) throws SAXException {
        printStream.println("skippedEntity: " + name);
    }
    
    public static void main(String[] args) throws Exception {
        org.xml.sax.XMLReader parser = 
            javax.xml.parsers.SAXParserFactory.newInstance().newSAXParser().getXMLReader();
        System.err.println("Parser: " + parser.getClass());
        parser.setContentHandler(new ExampleContentHandler());
        parser.parse(new java.io.File(args[0]).toURI().toString());
    }
}
