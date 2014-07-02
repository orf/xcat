import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import javax.xml.namespace.QName;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;

/**
  * Class XPathExampleDOM:
  *
  * This is a variant of the XPathExample application written to use DOM interfaces. Using the DOM
  * rather than Saxon's native tree model is not recommended unless the application has other reasons
  * to use the DOM model, but this application shows how it can be done when necessary.
  *
  * This class illustrates the use of the JAXP XPath API. It is a simple command-line application,
  * which prompts the user for a word, and replies with a list of all the lines containing that
  * word within a Shakespeare play.
  *
  *
  * @author Michael H. Kay (Michael.H.Kay@ntlworld.com)
  * @version Auguest 2005: modified to use DOM interfaces
  */

public class XPathExampleDOM implements XPathVariableResolver {

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
            System.err.println("Usage: java XPathExampleDOM input-file");
            System.exit(1);
        }
        XPathExampleDOM app = new XPathExampleDOM();
        app.go(args[0]);
    }

    /**
    * Run the application
    */

    public void go(String filename) throws Exception {

        XPathFactory xpf = XPathFactory.newInstance(XPathConstants.DOM_OBJECT_MODEL);

        // Uncomment the following line to force the Saxon XPath provider to be loaded
        // xpf = new XPathFactoryImpl();
        
        XPath xpe = xpf.newXPath();
        System.err.println("Loaded XPath Provider " + xpe.getClass().getName());

        // Build the source document.
        DocumentBuilderFactory dfactory = DocumentBuilderFactory.newInstance();
        System.err.println("Using DocumentBuilderFactory " + dfactory.getClass());

        dfactory.setNamespaceAware(true);

        DocumentBuilder docBuilder = dfactory.newDocumentBuilder();
            System.err.println("Using DocumentBuilder " + docBuilder.getClass());

        Node doc =
            docBuilder.parse(new InputSource(new File(filename).toURI().toString()));

        // Declare a variable resolver to return the value of variables used in XPath expressions
        xpe.setXPathVariableResolver(this);

        // Compile the XPath expressions used by the application

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
                NodeList matchedLines = (NodeList)findLine.evaluate(doc, XPathConstants.NODESET);

                // Process these lines
                boolean found = false;
                final int len = matchedLines.getLength();
                for (int i=0; i<len; i++) {

                    // Note that we have found at least one line
                    found = true;

                    // Get the next matching line
                    Node line = matchedLines.item(i);

                    // Find where it appears in the play
                    System.out.println('\n' + findLocation.evaluate(line));

                    // Output the name of the speaker and the content of the line
                    System.out.println(findSpeaker.evaluate(line) + ":  " + line.getTextContent());
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

}
