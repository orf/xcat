import com.saxonica.config.ProfessionalConfiguration;
import net.sf.saxon.option.jdom.DocumentWrapper;
import net.sf.saxon.TransformerFactoryImpl;
import net.sf.saxon.xpath.XPathEvaluator;
import org.jdom.Document;
import org.jdom.Element;
import org.jdom.JDOMException;
import org.jdom.input.SAXBuilder;

import javax.xml.transform.Templates;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import java.io.File;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;

/**
 * A simple example to show how SAXON can be used with a JDOM tree.
 * It is designed to be used with the source document books.xml and the
 * stylesheet total.xsl
 * @author Michael H. Kay
 */
public class JDOMExample {

    private JDOMExample() {}

    /**
     * Method main
     */
    public static void main(String argv[])
            throws TransformerException, XPathExpressionException,
                   JDOMException, IOException {

        if (argv.length == 2) {
            transform(argv[0], argv[1]);
        } else {
            System.err.println("Usage: JDOMExample source.xml style.xsl >out.xml");
        }

    }

    /**
     * Show (a) use of freestanding XPath expressions against the JDOM document, and
     * (b) the simplest possible transformation from system id to output stream.
     */

    public static void transform(String sourceID, String xslID)
            throws TransformerException, XPathExpressionException, JDOMException, IOException {

        // Get a TransformerFactory
        System.setProperty("javax.xml.transform.TransformerFactory",
                           "com.saxonica.config.ProfessionalTransformerFactory");
        TransformerFactory tfactory = TransformerFactory.newInstance();
        ProfessionalConfiguration config = (ProfessionalConfiguration)((TransformerFactoryImpl)tfactory).getConfiguration();

        // Build the JDOM document
        SAXBuilder builder = new SAXBuilder();
        Document doc = builder.build(new File(sourceID));

        // Give it a Saxon wrapper
        DocumentWrapper docw =
                new DocumentWrapper(doc, sourceID, config);

        // Retrieve all the ITEM elements
        XPathEvaluator xpath = new XPathEvaluator(config);
        XPathExpression exp = xpath.compile("//ITEM");
        List list = (List)exp.evaluate(docw, XPathConstants.NODESET);

        // For each of these, compute an additional attribute

        for (Iterator iter=list.iterator(); iter.hasNext();) {
            Element item = (Element)iter.next();
            String price = item.getChildText("PRICE");
            String quantity = item.getChildText("QUANTITY");
            try {
                double priceval = Double.parseDouble(price);
                double quantityval = Double.parseDouble(quantity);
                double value = priceval * quantityval;
                item.setAttribute("VALUE", ""+value);
            } catch (NumberFormatException err) {
                item.setAttribute("VALUE", "?");
            }
        }

        // Un-comment the following lines to get trace output from the transformation
        // tfactory.setAttribute(net.sf.saxon.lib.FeatureKeys.TRACE_LISTENER,
        //                       new net.sf.saxon.trace.XSLTTraceListener());

        // Compile the stylesheet

        Templates templates = tfactory.newTemplates(new StreamSource(xslID));
        Transformer transformer = templates.newTransformer();

        // Now do a transformation
        
        transformer.transform(docw, new StreamResult(System.out));

    }

    /**
     * Here is an extension function you can try calling from the XSLT stylesheet
     */

    public static int elementContentSize(Element element) {
        return element.getContentSize();
    }


}
