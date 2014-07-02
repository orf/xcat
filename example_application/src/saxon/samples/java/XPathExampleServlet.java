
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.namespace.QName;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.*;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

/**
 * Class XPathExample:
 * This class illustrates the use of the JAXP XPath API within a Java Servlet.
 * The application prompts the user for a word, and replies with a list of all the lines containing that
 * word within a Shakespeare play. The document containing the play is cached.
 * <p/>
 * In principle this application should run with any XPath provider that provides
 * access to DOM documents.
 *
 * @author Michael H. Kay
 * @version October 2006: rewritten as a Java servlet
 */

public class XPathExampleServlet extends HttpServlet {

    private XPathFactory xpathFactory;
    private DocumentBuilderFactory domFactory;

    private HashMap documentCache = new HashMap();
    // The key is an absolute URI identifying a source document
    // The value is the document node of the parsed document

    public void init() throws ServletException {
        System.setProperty("jaxp.debug", "true");
        System.err.println("Java version: " + System.getProperty("java.version"));
        System.out.println("Java version: " + System.getProperty("java.version"));

        System.setProperty("javax.xml.xpath.XPathFactory:http://java.sun.com/jaxp/xpath/dom", "net.sf.saxon.xpath.XPathFactoryImpl");

//        try {
        xpathFactory = XPathFactory.newInstance();
//        } catch (XPathFactoryConfigurationException e) {
//            throw new ServletException(e);
//        }

        try {
            domFactory = DocumentBuilderFactory.newInstance();
        } catch (FactoryConfigurationError e) {
            throw new ServletException(e);
        }

        System.err.println("Loaded XPathFactory " + xpathFactory.getClass().getName());
        System.err.println("Loaded DocumentBuilderFactory " + domFactory.getClass().getName());



//        InputStream ps = getClass().getResourceAsStream("xpath.properties");
//        if (ps == null) {
//            throw new ServletException("Failed to read LicenseParams.properties");
//        }
//        Properties props = new Properties();
//        try {
//            props.load(ps);
//        } catch (IOException err) {
//            throw new ServletException("Failure reading LicenseParams.properties");
//        }
    }

    private synchronized Document getDocument(String shortName) throws ServletException {
        Document doc = (Document) documentCache.get(shortName);
        if (doc != null) {
            return doc;
        }
        String path = getServletContext().getRealPath(shortName + ".xml");
        if (path == null) {
            throw new ServletException("Source file " + shortName + ".xml not found");
        }
        try {
            DocumentBuilder builder = domFactory.newDocumentBuilder();
            doc = builder.parse(new File(path));
        } catch (ParserConfigurationException e) {
            throw new ServletException(e);
        } catch (SAXException e) {
            throw new ServletException(e);
        } catch (IOException e) {
            throw new ServletException(e);
        }
        documentCache.put(shortName, doc);
        return doc;
    }


    protected void service(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        // Following is specific to Saxon: should be in a properties file
//        System.setProperty("javax.xml.xpath.XPathFactory:"+NamespaceConstant.OBJECT_MODEL_SAXON,
//                "net.sf.saxon.xpath.XPathFactoryImpl");

        try {
            final String word = request.getParameter("word");
            final String play = request.getParameter("play");

            Document doc = getDocument(play);

            // Create an XPath evaluation engine from the factory
            XPath xpe = xpathFactory.newXPath();

            // Declare a variable resolver to return the value of variables used in XPath expressions
            XPathVariableResolver variableResolver = new XPathVariableResolver() {
                /**
                 * <p>Find a variable in the set of available variables.</p>
                 * <p/>
                 * <p>If <code>variableName</code> is <code>null</code>, then a <code>NullPointerException</code> is thrown.</p>
                 *
                 * @param variableName The <code>QName</code> of the variable name.
                 * @return The variables value, or <code>null</code> if no variable named <code>variableName</code>
                 *         exists.  The value returned must be of a type appropriate for the underlying object model.
                 * @throws NullPointerException If <code>variableName</code> is <code>null</code>.
                 */
                public Object resolveVariable(QName variableName) {
                    if (variableName.getLocalPart().equals("word")) {
                        return word;
                    } else {
                        return null;
                    }
                }
            };
            xpe.setXPathVariableResolver(variableResolver);

            // Compile the XPath expressions used by the application

            //xpe.setNamespaceContext(this);
            XPathExpression playTitle =
                    xpe.compile("/PLAY/TITLE");
            XPathExpression findLine =
                    xpe.compile("//LINE[contains(., $word)]");
            XPathExpression findLocation =
                    xpe.compile("concat(ancestor::ACT/TITLE, ' ', ancestor::SCENE/TITLE)");
            XPathExpression findSpeaker =
                    xpe.compile("string(ancestor::SPEECH/SPEAKER[1])");

            PrintWriter out = new PrintWriter(response.getOutputStream());
            out.write("<html><head><title>Shakespeare search for '" + word + "'</title></head>");
            out.write("<body><h1>Shakespeare search for '" + word + "'</h1>");
            out.write("<p>You searched for all occurrences of '" + word + "' in <i>" +
                    playTitle.evaluate(doc, XPathConstants.STRING) + "</i>. The following matches were found:</p>");


            if (!word.equals("")) {

                // Find the lines containing the requested word
                Object matchedLinesResult = (Object) findLine.evaluate(doc, XPathConstants.NODESET);
                List matchedLines;
                if (matchedLinesResult instanceof List) {
                    matchedLines = (List) matchedLinesResult;
                } else if (matchedLinesResult instanceof NodeList) {
                    final int len = ((NodeList) matchedLinesResult).getLength();
                    matchedLines = new ArrayList(len);
                    for (int i = 0; i < len; i++) {
                        matchedLines.add(((NodeList) matchedLinesResult).item(i));
                    }
                } else {
                    throw new ServletException("Unknown class " +
                            matchedLinesResult.getClass() + " returned from XPath evaluator");
                }

                out.write("<ol>");

                // Process these lines
                boolean found = false;
                if (matchedLines != null) {
                    for (Iterator iter = matchedLines.iterator(); iter.hasNext();) {

                        // Note that we have found at least one line
                        found = true;

                        // Get the next matching line
                        Node line = (Node) iter.next();

                        out.write("<li>");
                        // Find where it appears in the play
                        out.write("<p>" + findLocation.evaluate(line) + "</p>");

                        // Output the name of the speaker and the content of the line
                        out.write("<p>" + findSpeaker.evaluate(line) + ":  " + line.getFirstChild().getNodeValue() + "</p>");
                        out.write("</li>");
                    }
                }

                out.write("</ol>");

                // If no lines were found, say so
                if (!found) {
                    out.write("<p>No lines were found containing the word '" + word + "'</p>");
                }
            }
            out.write("</body></html>");
            out.close();


        } catch (XPathException err) {
            throw new ServletException("XPath error", err);
        }

    }

}
