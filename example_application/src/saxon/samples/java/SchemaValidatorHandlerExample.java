import org.w3c.dom.TypeInfo;
import org.w3c.dom.ls.LSInput;
import org.w3c.dom.ls.LSResourceResolver;
import org.xml.sax.*;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.TypeInfoProvider;
import javax.xml.validation.ValidatorHandler;
import java.io.File;

/**
 * SchemaValidatorHandlerExample demonstrates the use of jaxp validation apis.
 *
 * This version was modified by Michael Kay from the sample application named SchemaValidator
 * issued with the JAXP 1.3 distribution. It has been changed to use a ValidatorHandler
 * and to display the types of elements and attributes as reported.
 *
 * The original file contained no explicit terms and conditions or copyright statement,
 * but it should be assumed that it is subject to the usual Apache rules.
 */

public class SchemaValidatorHandlerExample {

    /**
     * Class is never instantiated
     */
    private SchemaValidatorHandlerExample() {}

    /**
     * A custom SAX error handler
     */

    protected static class LocalErrorHandler implements ErrorHandler {

        private int errorCount = 0;

        /**
         * Report a non-fatal error
         * @param ex the error condition
         */
        public void error(SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
            errorCount++;
        }

        /**
         * Report a fatal error
         * @param ex the error condition
         */

        public void fatalError(SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
            errorCount++;
        }

        /**
         * Report a warning
         * @param ex the warning condition
         */
        public void warning(SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
        }

        /**
         * Get the error count
         * @return the number of errors reported, that is, the number of calls on error() or fatalError()
         */

        public int getErrorCount() {
            return errorCount;
        }

    }

    /**
     * Inner class to implement a resource resolver. This version always returns null, which
     * has the same effect as not supplying a resource resolver at all. The LSResourceResolver
     * is part of the DOM Level 3 load/save module.
     */

    protected static class Resolver implements LSResourceResolver{

        /**
         * Resolve a reference to a resource
         * @param type The type of resource, for example a schema, source XML document, or query
         * @param namespace The target namespace (in the case of a schema document)
         * @param publicId The public ID
         * @param systemId The system identifier (as written, possibly a relative URI)
         * @param baseURI The base URI against which the system identifier should be resolved
         * @return an LSInput object typically containing the character stream or byte stream identified
         * by the supplied parameters; or null if the reference cannot be resolved or if the resolver chooses
         * not to resolve it.
         */

        public LSInput resolveResource(String type, String namespace, String publicId, String systemId, String baseURI) {
            return null;
        }

    }

    /**
     * A ContentHandler to receive and display the results
     */

    public static class LocalContentHandler extends DefaultHandler {

        int indent = 0;
        private TypeInfoProvider provider;

        public LocalContentHandler(TypeInfoProvider provider) {
            this.provider = provider;
        }

        /**
         * Receive notification of the start of an element.
         */
        public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException {
            TypeInfo etype = provider.getElementTypeInfo();
            StringBuffer sb = new StringBuffer(100);
            for (int i=0; i<indent; i++) {
                sb.append("  ");
            }
            sb.append("Element " + qName);
            sb.append(" of type {" + etype.getTypeNamespace() + '}' + etype.getTypeName());
            System.out.println(sb.toString());
            for (int a=0; a<attributes.getLength(); a++) {
                TypeInfo atype = provider.getAttributeTypeInfo(a);
                boolean spec = provider.isSpecified(a);
                sb.setLength(0);
                for (int i=0; i<indent+2; i++) {
                    sb.append("  ");
                }
                sb.append("Attribute " + attributes.getQName(a) + (spec ? " (specified)" : (" (defaulted)")));
                if (atype == null) {
                    sb.append(" of unknown type");
                } else {
                    sb.append(" of type {" + atype.getTypeNamespace() + '}' + atype.getTypeName());
                }
                System.out.println(sb.toString());
            }
            indent++;
        }

        /**
         * Receive notification of the end of an element.
         */
        public void endElement(String uri, String localName, String qName) throws SAXException {
            indent--;
        }
    }

    /**
     * Main entry point. Expects two arguments: the schema document, and the source document.
     * Allows "--" as the schema document, indicating that the schema is identified by xsi:schemaLocation
     * @param args
     */
    public static void main(String [] args) {
        try {
            if(args.length != 2){
                printUsage();
                return;
            }

            SchemaFactory schemaFactory;

            // Set a system property to force selection of the Saxon SchemaFactory implementation
            // This is commented out because it shouldn't be necessary if Saxon-EE is on the classpath;
            // but in the event of configuration problems, try reinstating it.

//            System.setProperty("javax.xml.validation.SchemaFactory:http://www.w3.org/2001/XMLSchema",
//                    "com.saxonica.jaxp.SchemaFactoryImpl");

            schemaFactory = SchemaFactory.newInstance("http://www.w3.org/2001/XMLSchema");
            //schemaFactory.setProperty(FeatureKeys.VALIDATION_WARNINGS, Boolean.TRUE);

            System.err.println("Loaded schema validation provider " + schemaFactory.getClass().getName());

            LocalErrorHandler errorHandler = new LocalErrorHandler();
            schemaFactory.setErrorHandler(errorHandler);
            //create a grammar object.
            Schema schemaGrammar;

            if (args[0].equals("--")) {
                // in this case, the schema must be identified using xsi:schemaLocation
                schemaGrammar = schemaFactory.newSchema();
            } else {
                schemaGrammar = schemaFactory.newSchema(new File(args[0]));
                System.err.println("Created Grammar object for schema : "+args[0]);
            }

            Resolver resolver = new Resolver();

            //create a validator to validate against the schema.
            ValidatorHandler schemaValidator = schemaGrammar.newValidatorHandler();
            schemaValidator.setResourceResolver(resolver);
            schemaValidator.setErrorHandler(errorHandler);
            schemaValidator.setContentHandler(new LocalContentHandler(schemaValidator.getTypeInfoProvider()));

            System.err.println("Validating "+args[1] +" against grammar "+args[0]);
            SAXParserFactory parserFactory = SAXParserFactory.newInstance();
            parserFactory.setNamespaceAware(true);
            SAXParser parser = parserFactory.newSAXParser();
            XMLReader reader = parser.getXMLReader();
            reader.setContentHandler(schemaValidator);
            reader.parse(new InputSource(new File(args[1]).toURI().toString()));

            // Note: It appears Xerces exits normally if validation errors were found. Saxon throws an exception.

            int errorCount = errorHandler.getErrorCount();
            if (errorCount == 0) {
                System.err.println("Validation successful");
            } else {
                System.err.println("Validation unsuccessful: " + errorCount + " error" + (errorCount==1?"":"s"));
            }
        } catch (SAXException saxe) {
            exit(1, "Error: " + saxe.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            exit(2, "Fatal Error: " + e);
        }
    }

    private static void exit(int errCode, String msg) {
        System.err.println(msg);
        System.exit(errCode);
    }

    public static void printUsage(){
        System.err.println("Usage : java SchemaValidatorHandlerExample (<schemaFile>|--) <xmlFile>");
    }
}
