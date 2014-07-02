import net.sf.saxon.Configuration;
import net.sf.saxon.Controller;
import net.sf.saxon.expr.instruct.UserFunction;
import net.sf.saxon.om.*;
import net.sf.saxon.query.DynamicQueryContext;
import net.sf.saxon.query.QueryResult;
import net.sf.saxon.query.StaticQueryContext;
import net.sf.saxon.query.XQueryExpression;
import net.sf.saxon.trans.XPathException;
import net.sf.saxon.value.Int64Value;
import net.sf.saxon.value.Value;
import net.sf.saxon.xpath.XPathEvaluator;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMResult;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.Properties;


/**
 * Some examples to show how the old Saxon XQuery API should be used.
 * This is legacy: the s9appi interface should be used in preference.
 */
public class QueryAPIExamples {

    /**
     * Class is not instantiated, so give it a private constructor
     */
    private QueryAPIExamples() {
    }

    /**
     * Method main
     * @param argv Command line arguments
     * <p>Format: QueryAPIExamples [testname]</p>
     * <p>where testname is one of the tests (for their names, see the source code)</p>
     */
    public static void main(String argv[]) {

        String test = "all";
        if (argv.length > 0) {
            test = argv[0];
        }

        if (test.equals("all") || test.equals("toStreamResult")) {
            System.out.println("\n\n==== toStreamResult ====");

            try {
                exampleToStreamResult();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toSingleton")) {
            System.out.println("\n\n==== toSingleton ====");

            try {
                exampleToSingleton();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toDOM")) {
            System.out.println("\n\n==== toDOM ====");

            try {
                exampleToDOM();
            } catch (Exception ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toSequence")) {
            System.out.println("\n\n==== toSequence ====");

            try {
                exampleToSequence();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toSerializedSequence")) {
            System.out.println("\n\n==== toSerializedSequence ====");

            try {
                exampleToSerializedSequence();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toWrappedSequence")) {
            System.out.println("\n\n==== toWrappedSequence ====");

            try {
                exampleToWrappedSequence();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("toHTMLFile")) {
            System.out.println("\n\n==== toHTMLFile ====");

            try {
                exampleToHTMLFile();
            } catch (XPathException ex) {
                handleException(ex);
            } catch (IOException ex) {
                System.err.println("Problem reading/writing files. Check that the current directory is the 'samples' directory");
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("withParam")) {
            System.out.println("\n\n==== withParam ====");

            try {
                exampleWithParam();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("pipeline")) {
            System.out.println("\n\n==== pipeline ====");

            try {
                examplePipeline();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }

        if (test.equals("all") || test.equals("directFunction")) {
            System.out.println("\n\n==== directFunction ====");

            try {
                exampleDirectFunction();
            } catch (XPathException ex) {
                handleException(ex);
            }
        }


    }

    /**
     * Show a query producing a document as its result and serializing this
     * directly to System.out
     */

    public static void exampleToStreamResult() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("<a b='c'>{5+2}</a>");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        final Properties props = new Properties();
        props.setProperty(OutputKeys.METHOD, "xml");
        props.setProperty(OutputKeys.INDENT, "yes");
        exp.run(dynamicContext, new StreamResult(System.out), props);
    }

    /**
     * Show a query producing a single atomic value as its result and returning the value
     * to the Java application
     */

    public static void exampleToSingleton() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("avg(for $i in 1 to 10 return $i*$i)");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        final BigDecimal result = (BigDecimal)exp.evaluateSingle(dynamicContext);
        System.out.println(result);

    }

    /**
     * Show a query producing a DOM as its output. The DOM is then serialized using
     * an identity transform
     */

    public static void exampleToDOM() throws TransformerException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("<a xmlns='http://a/uri' xmlns:a='another.uri'>text</a>");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        DOMResult result = new DOMResult();
        exp.run(dynamicContext, result, new Properties());

        // now serialize the DOM

        Transformer identity = TransformerFactory.newInstance().newTransformer();
        identity.transform(new DOMSource(result.getNode()), new StreamResult(System.out));

    }

    /**
     * Show a query producing a sequence as its result and returning the sequence
     * to the Java application in the form of an iterator. For each item in the
     * result, its string value is output.
     */

    public static void exampleToSequence() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("for $i in 1 to 10 return ($i * $i)");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        final SequenceIterator iter = exp.iterator(dynamicContext);
        while (true) {
            Item item = iter.next();
            if (item == null) {
                break;
            }
            System.out.println(item.getStringValue());
        }

    }

    /**
     * Show a query producing a sequence as its result and returning the sequence
     * to the Java application in the form of an iterator. The sequence is treated
     * as if it were the content of a document{...} constructor. Note that it must
     * not contain free-standing attribute nodes.
     */

    public static void exampleToSerializedSequence() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("<doc><chap><a>3</a></chap></doc>//a, <b>4</b>, 19");
        Properties props = new Properties();
        props.setProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        final SequenceIterator iter = exp.iterator(dynamicContext);
        QueryResult.serializeSequence(iter, config, System.out, props);
    }

    /**
     * Show a query producing a sequence as its result and returning the sequence
     * to the Java application in the form of an iterator. The sequence is then
     * output by wrapping the items in a document, with wrapping elements indicating
     * the type of each item, and serializing the resulting document.
     */

    public static void exampleToWrappedSequence() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("<doc><chap><a>3</a></chap></doc>//a, <b>4</b>, attribute c {5}, 19");
        Properties props = new Properties();
        props.setProperty(OutputKeys.OMIT_XML_DECLARATION, "no");
        props.setProperty(OutputKeys.INDENT, "yes");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        final SequenceIterator iter = exp.iterator(dynamicContext);
        final DocumentInfo doc = QueryResult.wrap(iter, config);
        QueryResult.serialize(doc, new StreamResult(System.out), props);
    }


    /**
     * Show how to run a query that is read from a file and that serializes its output
     * as HTML to another file. The input to the query (the initial value of the context
     * node) is supplied as the content of another file.
     */

    public static void exampleToHTMLFile() throws XPathException, IOException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery(new FileReader("query/books-to-html.xq"));
        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        dynamicContext.setContextItem(config.buildDocument(new StreamSource("data/books.xml")));
        final Properties props = new Properties();
        props.setProperty(OutputKeys.METHOD, "html");
        props.setProperty(OutputKeys.DOCTYPE_PUBLIC, "-//W3C//DTD HTML 4.01 Transitional//EN");
        exp.run(dynamicContext, new StreamResult(new File("booklist.html")), props);
    }

    /**
     * Show a query that takes a parameter (external variable) as input.
     * The query produces a single atomic value as its result and returns the value
     * to the Java application. For the types of value that may be returned, and
     * their mapping to XPath data types, see {@link XPathEvaluator#evaluate}
     */

    public static void exampleWithParam() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp = sqc.compileQuery("declare variable $in as xs:integer external;" +
                "$in * $in");

        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        dynamicContext.setParameterValue("in", Int64Value.makeIntegerValue(17));
        final Long result = (Long)exp.evaluateSingle(dynamicContext);
        System.out.println("17 * 17 = " + result);

    }

    /**
     * Show how to run two queries in tandem. The second query is applied to the
     * results of the first.
     */

    public static void examplePipeline() throws XPathException {
        final Configuration config = new Configuration();

        // Compile the first query
        final StaticQueryContext sqc1 = config.newStaticQueryContext();
        final XQueryExpression exp1 = sqc1.compileQuery("declare variable $in as xs:integer external;" +
                "document{ <a>{$in * $in}</a> }");

        // Compile the second query (each query should have its own static context)
        final StaticQueryContext sqc2 = config.newStaticQueryContext();
        final XQueryExpression exp2 = sqc2.compileQuery("/a + 5");

        // Run the first query
        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
        dynamicContext.setParameterValue("in", Int64Value.makeIntegerValue(3));
        final NodeInfo doc = (NodeInfo)exp1.evaluateSingle(dynamicContext);

        // Run the second query
        dynamicContext.clearParameters();
        dynamicContext.setContextItem(doc);
        final Object result = exp2.evaluateSingle(dynamicContext);
        System.out.println("3*3 + 5 = " + result);
        // The result is actually a java.lang.Double
    }

    /**
     * Show a direct call from the Java application to a function defined in the
     * Query. This is a very efficient way of invoking a query, but it does minimal
     * checking of the supplied arguments
     */

    public static void exampleDirectFunction() throws XPathException {
        final Configuration config = new Configuration();
        final StaticQueryContext sqc = config.newStaticQueryContext();
        final XQueryExpression exp1 = sqc.compileQuery("declare namespace f='f.ns';" +
                "declare function f:t1($v1 as xs:integer, $v2 as xs:untypedAtomic*) { " +
                "   $v1 div $v2" +
                "};" +
                "10");

        final UserFunction fn1 = exp1.getStaticContext().getUserDefinedFunction("f.ns", "t1", 2);
        if (fn1 == null) {
            throw new IllegalStateException("Function f:t1() not found");
        }
        final Controller controller = exp1.newController();
        final Value[] arglist = new Value[2];
        arglist[0] = new Int64Value(10);
        for (int i = 3; i < 10; i++) {
            arglist[1] = new Int64Value(i);
            final ValueRepresentation result = fn1.call(arglist, controller);
            System.out.println(arglist[0] + " div " + arglist[1] + " = " + result);
        }
    }

    /**
     * Handle an exception thrown while running one of the examples
     *
     * @param ex the exception
     */
    private static void handleException(Exception ex) {
        System.out.println("EXCEPTION: " + ex);
        ex.printStackTrace();
    }

}

//
// The contents of this file are subject to the Mozilla Public License Version 1.0 (the "License");
// you may not use this file except in compliance with the License. You may obtain a copy of the
// License at http://www.mozilla.org/MPL/
//
// Software distributed under the License is distributed on an "AS IS" basis,
// WITHOUT WARRANTY OF ANY KIND, either express or implied.
// See the License for the specific language governing rights and limitations under the License.
//
// The Original Code is: all this file.
//
// The Initial Developer of the Original Code is Michael H. Kay.
//
// Portions created by (your name) are Copyright (C) (your legal entity). All Rights Reserved.
//
// Contributor(s): none.
//
