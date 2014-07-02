
import org.w3c.dom.ls.LSInput;
import org.w3c.dom.ls.LSResourceResolver;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.File;

/**
 * SchemaValidatorExample demonstrates the use of jaxp validation apis.
 *
 * This version was modified by Michael Kay from the version (named SchemaValidator)
 * issued with the JAXP 1.3 distribution. It has been changed to set system properties
 * that force loading of Saxon, to improve the error reporting, and to improve the
 * comments.
 *
 * The original file contained no explicit terms and conditions or copyright statement,
 * but it should be assumed that it is subject to the usual Apache rules.
 */

public class SchemaValidatorExample {

    private SchemaValidatorExample() {
        // the class is never instantiated
    }

    /**
     * A custom SAX error handler
     */

    protected static class Handler implements ErrorHandler {

        /**
         * Report a non-fatal error
         * @param ex the error condition
         */
        public void error(SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
        }

        /**
         * Report a fatal error
         * @param ex the error condition
         */

        public void fatalError(SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
        }

        /**
         * Report a warning
         * @param ex the warning condition
         */
        public void warning(org.xml.sax.SAXParseException ex) {
            System.err.println("At line " + ex.getLineNumber() + " of " + ex.getSystemId() + ':');
            System.err.println(ex.getMessage());
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
     * Main entry point. Expects two arguments: the schema document, and the source document.
     * @param args
     */
    public static void main(String [] args) {
        try {
            if(args.length != 2){
                printUsage();
                return;
            }

            Handler handler = new Handler();

            SchemaFactory schemaFactory;

            // Set a system property to force selection of the Saxon SchemaFactory implementation
            // This is commented out because it shouldn't be necessary if Saxon-EE is on the classpath;
            // but in the event of configuration problems, try reinstating it.

//            System.setProperty("javax.xml.validation.SchemaFactory:http://www.w3.org/2001/XMLSchema",
//                    "com.saxonica.jaxp.SchemaFactoryImpl");

            // Alternatively, reinstate the following line to instantiate the SchemaFactory directly

//          schemaFactory = new com.saxonica.jaxp.SchemaFactoryImpl();

            schemaFactory = SchemaFactory.newInstance("http://www.w3.org/2001/XMLSchema");
            System.err.println("Loaded schema validation provider " + schemaFactory.getClass().getName());

            schemaFactory.setErrorHandler(handler);

            // create a grammar object.
            Schema schemaGrammar;
            if (args[0].equals("--")) {
                // in this case, the schema must be identified using xsi:schemaLocation
                schemaGrammar = schemaFactory.newSchema();
            } else {
                schemaGrammar = schemaFactory.newSchema(new File(args[0]));
                System.err.println("Created Grammar object for schema : "+args[0]);
            }

            Resolver resolver = new Resolver();
            //create a validator to validate against grammar sch.
            Validator schemaValidator = schemaGrammar.newValidator();
            schemaValidator.setResourceResolver(resolver);
            schemaValidator.setErrorHandler(handler);

            System.err.println("Validating "+args[1] +" against grammar "+args[0]);
            //validate xml instance against the grammar.
            schemaValidator.validate(new StreamSource(args[1]));

            System.err.println("Validation successful");
        } catch (SAXException saxe) {
            exit(1, "Error: " + saxe.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            exit(2, "Fatal Error: " + e);
        }
    }

    /**
     *
     * @param errCode
     * @param msg
     */
    public static void exit(int errCode, String msg) {
        System.err.println(msg);
        System.exit(errCode);
    }

    public static void printUsage(){
        System.err.println("Usage : SchemaValidatorExample <schemaFile> <xmlFile>");
    }
}
