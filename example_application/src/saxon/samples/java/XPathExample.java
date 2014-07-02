import net.sf.saxon.lib.NamespaceConstant;
import net.sf.saxon.om.NodeInfo;
import net.sf.saxon.xpath.XPathEvaluator;
import org.xml.sax.InputSource;

import javax.xml.namespace.NamespaceContext;
import javax.xml.namespace.QName;
import javax.xml.transform.sax.SAXSource;
import javax.xml.xpath.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.Iterator;
import java.util.List;

/**
  * Class XPathExample:
  * This class illustrates the use of the JAXP XPath API. It is a simple command-line application,
  * which prompts the user for a word, and replies with a list of all the lines containing that
  * word within a Shakespeare play.
  *
  *
  * @author Michael H. Kay (Michael.H.Kay@ntlworld.com)
  * @version October 2004: rewritten to use the JAXP API
  */

public class XPathExample implements XPathVariableResolver, NamespaceContext {

    private String currentWord;

    /**
      * main()<BR>
      * Expects one argument, the input filename<BR>
      */

    public static void main (String args[])
    throws Exception
    {
        // Check the command-line arguments

        if (args.length != 1) {
            System.err.println("Usage: java XPathExample input-file");
            System.exit(1);
        }
        XPathExample app = new XPathExample();
        app.go(args[0]);
    }

    /**
    * Run the application
    */

    public void go(String filename) throws Exception {

        // Following is specific to Saxon: should be in a properties file
        System.setProperty("javax.xml.xpath.XPathFactory:"+NamespaceConstant.OBJECT_MODEL_SAXON,
              "net.sf.saxon.xpath.XPathFactoryImpl");

        XPathFactory xpf = XPathFactory.newInstance(NamespaceConstant.OBJECT_MODEL_SAXON);
        XPath xpe = xpf.newXPath();
        System.err.println("Loaded XPath Provider " + xpe.getClass().getName());

        // Build the source document. This is outside the scope of the XPath API, and
        // is therefore Saxon-specific.
        InputSource is = new InputSource(new File(filename).toURL().toString());
        SAXSource ss = new SAXSource(is);
        NodeInfo doc = ((XPathEvaluator)xpe).setSource(ss);

        // Declare a variable resolver to return the value of variables used in XPath expressions
        xpe.setXPathVariableResolver(this);

        // Compile the XPath expressions used by the application

        //xpe.setNamespaceContext(this);

        XPathExpression findLine =
            xpe.compile("//LINE[contains(., $word)]");
        XPathExpression findLocation =
            xpe.compile("concat(ancestor::ACT/TITLE, ' ', ancestor::SCENE/TITLE)");
        XPathExpression findSpeaker =
            xpe.compile("string(ancestor::SPEECH/SPEAKER[1])");

        // Create a reader for reading input from the console

        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));

        // Loop until the user enters "." to end the application

        while (true) {

            // Prompt for input
            System.out.println("\n>>>> Enter a word to search for, or '.' to quit:\n");

            // Read the input
            String word = in.readLine().trim();
            if (word.equals(".")) {
                break;
            }
            if (!word.equals("")) {

                // Set the value of the XPath variable
                currentWord = word;

                // Find the lines containing the requested word
                List matchedLines = (List)findLine.evaluate(doc, XPathConstants.NODESET);

                // Process these lines
                boolean found = false;
                if (matchedLines != null) {
                    for (Iterator iter = matchedLines.iterator(); iter.hasNext();) {

                        // Note that we have found at least one line
                        found = true;

                        // Get the next matching line
                        NodeInfo line = (NodeInfo)iter.next();

                        // Find where it appears in the play
                        System.out.println('\n' + findLocation.evaluate(line));

                        // Output the name of the speaker and the content of the line
                        System.out.println(findSpeaker.evaluate(line) + ":  " + line.getStringValue());
                    }
                }

                // If no lines were found, say so
                if (!found) {
                    System.err.println("No lines were found containing the word '" + word + '\'');
                }
            }
        }

        // Finish when the user enters "."
        System.out.println("Finished.");
    }

    /**
     * This class serves as a variable resolver. The only variable used is $word.
     * @param qName the name of the variable required
     * @return the current value of the variable
     */

    public Object resolveVariable(QName qName) {
        if (qName.getLocalPart().equals("word")) {
            return currentWord;
        } else {
            return null;
        }
    }

    /**
     * This class serves as a namespace context.
     */

    /**
     * <p>Get Namespace URI bound to a prefix in the current scope.</p>
     * @param prefix prefix to look up
     * @return Namespace URI bound to prefix in the current scope
     */

    public String getNamespaceURI(String prefix) {
        System.err.println("Looking up: " + prefix);
        if (prefix.equals("saxon")) {
            return "http://saxon.sf.net/";
        } else {
            return null;
        }
    }

    /**
     * <p>Get prefix bound to Namespace URI in the current scope.</p>
     * @param namespaceURI URI of Namespace to lookup
     * @return prefix bound to Namespace URI in current context
     */

    public String getPrefix(String namespaceURI) {
        return null;  // not used by Saxon
    }

    /**
     * <p>Get all prefixes bound to a Namespace URI in the current
     * scope.</p>
     * @param namespaceURI URI of Namespace to lookup
     * @return <code>Iterator</code> for all prefixes bound to the
     *         Namespace URI in the current scope
     */
    public Iterator getPrefixes(String namespaceURI) {
        return null;  // not used by Saxon
    }

}
