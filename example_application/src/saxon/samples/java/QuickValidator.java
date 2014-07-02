
import com.saxonica.config.EnterpriseTransformerFactory;
import net.sf.saxon.lib.FeatureKeys;
import net.sf.saxon.lib.Validation;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.sax.SAXResult;
import javax.xml.transform.stream.StreamSource;
import java.io.File;

/**
 * This class performs schema validation of a source document against the
 * schema specified in its xsi:schemaLocation attribute, or a schema supplied on the command line
 */

public class QuickValidator {
    
    private QuickValidator() {
    }

    /**
     * Usage: java QuickValidator source.xml schema.xsd
     * @param args first argument is the source file; second is the schema
     * @throws Exception
     */

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("No source file supplied");
        }
        try {
            System.setProperty("javax.xml.transform.TransformerFactory",
                               "com.saxonica.config.EnterpriseTransformerFactory");
            TransformerFactory factory = TransformerFactory.newInstance();
            System.err.println("TransformerFactory class: " + factory.getClass().getName());
            factory.setAttribute(FeatureKeys.SCHEMA_VALIDATION, new Integer(Validation.STRICT));
            factory.setAttribute(FeatureKeys.VALIDATION_WARNINGS, Boolean.TRUE);
            if (args.length > 1) {
                StreamSource schema = new StreamSource(new File(args[1]).toURI().toString());
                ((EnterpriseTransformerFactory)factory).addSchema(schema);
            }
            Transformer trans = factory.newTransformer();
            StreamSource source = new StreamSource(new File(args[0]).toURI().toString());
            SAXResult sink = new SAXResult(new DefaultHandler());
            trans.transform(source, sink);
        } catch (TransformerException err) {
            System.err.println("Validation failed: " + err.getMessage());
        }
    }

}
