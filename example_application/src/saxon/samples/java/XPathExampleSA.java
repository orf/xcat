import com.saxonica.config.EnterpriseXPathFactory;
import net.sf.saxon.om.NodeInfo;
import net.sf.saxon.xpath.XPathEvaluator;
import org.xml.sax.InputSource;

import javax.xml.XMLConstants;
import javax.xml.namespace.NamespaceContext;
import javax.xml.namespace.QName;
import javax.xml.transform.sax.SAXSource;
import javax.xml.transform.stream.StreamSource;
import javax.xml.xpath.*;
import java.io.File;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Class XPathExampleSA:
 * This class illustrates the use of the JAXP XPath API, extended by Saxon to allow schema-aware XPath 2.0
 * processing.
 * <p>
 * The program is designed to run against the sample file books.xml. It produces a list of all books over 2cm
 * thick that were published during the previous year.
 *
 * @author Michael H. Kay (Michael.H.Kay@ntlworld.com)
 * @version September 2005: first version
 */

public class XPathExampleSA implements XPathVariableResolver, XPathFunctionResolver, NamespaceContext {



    /**
      * main()<BR>
      * Expects two arguments, the input filename, and the schema for the input document<BR>
      */

    public static void main (String args[])
    throws Exception
    {
        // Check the command-line arguments

        if (args.length != 2) {
            System.err.println("Usage: java XPathExampleSA input-file schema");
            System.exit(1);
        }
        XPathExampleSA app = new XPathExampleSA();
        app.go(args[0], args[1]);
    }

    /**
    * Run the application
    */

    public void go(String filename, String schema) throws Exception {

        // Load an XPath factory. This should load the Saxon schema-aware factory if everything has
        // been configured correctly.

        //XPathFactory xpf = XPathFactory.newInstance(NamespaceConstant.OBJECT_MODEL_SAXON);
        XPathFactory xpf = new EnterpriseXPathFactory();
        XPath xpe = xpf.newXPath();
        System.err.println("Loaded XPath Provider " + xpe.getClass().getName() +
                " using factory " + xpf.getClass().getName());

        // Request the processor to perform validation of input documents

        xpf.setFeature("http://saxon.sf.net/feature/schema-validation", true);

        // Check that the processor really is schema-aware

        if (!xpf.getFeature("http://saxon.sf.net/feature/schema-validation")) {
            System.err.println("Error: this XPath provider is not schema-aware (probably a license file problem)");
            System.exit(2);
        }

        // Declare a variable resolver to return the value of variables used in XPath expressions
        xpe.setXPathVariableResolver(this);

        // Declare a function resolver to handle the function call in the XPath expression
        xpe.setXPathFunctionResolver(this);

        // Import the schema for types references in the XPath expression
        ((XPathEvaluator)xpe).importSchema(new StreamSource(schema));

        // Build the source document. This is outside the scope of the XPath API, and
        // is therefore Saxon-specific.
        InputSource is = new InputSource(new File(filename).toURI().toString());
        SAXSource ss = new SAXSource(is);
        NodeInfo doc = ((XPathEvaluator)xpe).setSource(ss);


        // Compile the XPath expressions used by the application

        xpe.setNamespaceContext(this);

        XPathExpression findBooks = null;
        try {
            findBooks = xpe.compile("//schema-element(ITEM)" +
                                    "[PUB-DATE gt (current-date() - xs:yearMonthDuration($age))]" +
                                    "[min((f:toCentimetres(data(DIMENSIONS) treat as dimensionType*, " +
                                           "data(DIMENSIONS/@UNIT)))) gt $thickness]" +
                                    "/TITLE");
        } catch (XPathExpressionException e) {
            System.err.println("Error in XPath Expression");
            System.err.println(e.getCause().getMessage());
            System.exit(2);
        }

        // Find the titles matching the specified criteria
        List matchedLines = (List)findBooks.evaluate(doc, XPathConstants.NODESET);

        // Process these lines
        boolean found = false;
        if (matchedLines != null) {
            for (Iterator iter = matchedLines.iterator(); iter.hasNext();) {

                // Note that we have found at least one line
                found = true;

                // Get the next matching title
                NodeInfo book = (NodeInfo)iter.next();

                // Display the title
                System.out.println(book.getStringValue());

            }
        }

        // If no books were found, say so
        if (!found) {
            System.err.println("No books were found matching the criteria");
        }

        // Finish 
        System.out.println("Finished.");
    }

    /**
     * This class serves as a variable resolver. The only variables used are $age and $thickness.
     * @param qName the name of the variable required
     * @return the current value of the variable
     */

    public Object resolveVariable(QName qName) {
        if (qName.getLocalPart().equals("age")) {
            return "P6Y";
        } else if (qName.getLocalPart().equals("thickness")) {
            return new BigDecimal("2.0");
        } else {
            return null;
        }
    }

    /**
     * This class serves as a function resolver. The only function used is f:toCentimetres.
     * @param qName the name of the variable required
     * @return the current value of the variable
     */

    public XPathFunction resolveFunction(QName qName, int arity) {
        if (qName.getLocalPart().equals("toCentimetres")) {
            return new ToCentimetres();
        } else {
            return null;
        }
    }

    /**
     * <p>Get Namespace URI bound to a prefix in the current scope.</p>
     * @param prefix prefix to look up
     * @return Namespace URI bound to prefix in the current scope
     */
    public String getNamespaceURI(String prefix) {
        if (prefix.equals("f")) {
            return "http://localhost/functions";
        } else if (prefix.equals("xs")) {
            return XMLConstants.W3C_XML_SCHEMA_NS_URI;
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
        if (namespaceURI.equals("")) {
            return "f";
        } else {
            return null;
        }
    }

    /**
     * <p>Get all prefixes bound to a Namespace URI in the current
     * scope.</p>
     * @param namespaceURI URI of Namespace to lookup
     * @return <code>Iterator</code> for all prefixes bound to the
     *         Namespace URI in the current scope
     */
    public Iterator getPrefixes(String namespaceURI) {
        return null;
        // not needed by Saxon implementation
    }


    public static class ToCentimetres implements XPathFunction {
        /**
         * <p>Evaluate the function with the specified arguments.</p>
         *
         * @param args The arguments, <code>null</code> is a valid value.
         * @return The result of evaluating the <code>XPath</code> function as an <code>Object</code>.
         * @throws javax.xml.xpath.XPathFunctionException
         *          If <code>args</code> cannot be evaluated with this <code>XPath</code> function.
         */
        public Object evaluate(List args) throws XPathFunctionException {
            List dimensions = (List)args.get(0);
            String units = (String)args.get(1);
            if (units.equals("cm")) {
                return dimensions;
            } else if (units.equals("in")) {
                List newDimensions = new ArrayList(dimensions.size());
                for (int i=0; i<dimensions.size(); i++) {
                    newDimensions.add(((BigDecimal)dimensions.get(i)).multiply(INCHES_TO_CM));
                }
                return newDimensions;
            } else {
                throw new XPathFunctionException("Unknown units value: " + units);
            }
        }

        private static BigDecimal INCHES_TO_CM = new BigDecimal(2.54);
    }

}
