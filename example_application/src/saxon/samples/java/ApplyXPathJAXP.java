/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2002-2003 The Apache Software Foundation.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xalan" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, Lotus
 * Development Corporation., http://www.lotus.com.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */
// This file uses 4 space indents, no tabs.

import net.sf.saxon.lib.NamespaceConstant;
import org.jdom.input.SAXBuilder;
import org.xml.sax.InputSource;

import javax.xml.namespace.NamespaceContext;
import javax.xml.namespace.QName;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.stream.StreamSource;
import javax.xml.xpath.*;
import java.io.File;
import java.io.FileInputStream;
import java.util.Iterator;
import java.util.List;


/**
 * Very basic utility for applying the  XPath API in JAXP 1.3
 * to an xml file and printing information about the execution of the XPath object
 * and the nodes it finds.
 * Takes 2 or 3 arguments:
 * (1) an xml filename
 * (2) an XPath expression to apply to the file
 * (3) (optionally) short name of the object model to be used: "saxon" | "dom" | "jdom" | "xom"
 * Examples:
 * java ApplyXPathJAXP foo.xml /
 * java ApplyXPathJAXP foo.xml /doc/name[1]/@last
 * <p/>
 * This version modified by Michael Kay to allow testing of additional
 * features of the interface.
 *
 * The XPath expression may use:
 * (a) A namespace prefix f which is bound to the namespace http://localhost/f
 * (b) A variable $f:pi whose value is the Double pi
 * (c) A function f:sqrt(x) that calculates the square root of its argument x
 *
 * @see javax.xml.xpath.XPath
 */
public class ApplyXPathJAXP {
    protected String filename = null;
    protected String xpathExpressionStr = null;
    protected String objectModel = null;

    /**
     * Process input args and execute the XPath.
     */
    public void doMain(String[] args)
            throws Exception {
        filename = args[0];
        xpathExpressionStr = args[1];
        String om = "saxon";
        if (args.length > 2) {
            om = args[2];
        }
        if (om.equals("saxon")) {
            objectModel = NamespaceConstant.OBJECT_MODEL_SAXON;
        } else if (om.equals("dom")) {
            objectModel = XPathConstants.DOM_OBJECT_MODEL;
        } else if (om.equals("jdom")) {
            objectModel = NamespaceConstant.OBJECT_MODEL_JDOM;
        } else if (om.equals("dom4j")) {
            objectModel = NamespaceConstant.OBJECT_MODEL_DOM4J;
        } else if (om.equals("xom")) {
            objectModel = NamespaceConstant.OBJECT_MODEL_XOM;
        } else {
            System.err.println("Unknown object model " + args[2]);
            return;
        }

        if ((filename != null) && (filename.length() > 0)
                && (xpathExpressionStr != null) && (xpathExpressionStr.length() > 0)) {
            // Tell that we're loading classes and parsing, so the time it
            // takes to do this doesn't get confused with the time to do
            // the actual query and serialization.
            System.out.println("Loading classes, parsing " + filename + ", and setting up serializer");

            // Following is specific to Saxon: should be in a properties file
            System.setProperty("javax.xml.xpath.XPathFactory:"+NamespaceConstant.OBJECT_MODEL_SAXON,
                    "net.sf.saxon.xpath.XPathFactoryImpl");
            System.setProperty("javax.xml.xpath.XPathFactory:"+XPathConstants.DOM_OBJECT_MODEL,
                    "net.sf.saxon.xpath.XPathFactoryImpl");
            System.setProperty("javax.xml.xpath.XPathFactory:"+ NamespaceConstant.OBJECT_MODEL_JDOM,
                    "net.sf.saxon.xpath.XPathFactoryImpl");
            System.setProperty("javax.xml.xpath.XPathFactory:"+NamespaceConstant.OBJECT_MODEL_XOM,
                    "net.sf.saxon.xpath.XPathFactoryImpl");
            System.setProperty("javax.xml.xpath.XPathFactory:"+NamespaceConstant.OBJECT_MODEL_DOM4J,
                    "net.sf.saxon.xpath.XPathFactoryImpl");



            // Get a instance of XPathFactory with ObjectModel URL parameter. If no parameter
            // is mentioned then default DOM Object Model is used
            XPathFactory xpathFactory = XPathFactory.newInstance(objectModel);
            XPath xpath = xpathFactory.newXPath();



            Object document = null;
            if (objectModel.equals(NamespaceConstant.OBJECT_MODEL_SAXON)) {
                document = new StreamSource(new File(filename));

            } else if (objectModel.equals(XPathConstants.DOM_OBJECT_MODEL)) {
                InputSource in = new InputSource(new FileInputStream(filename));
                in.setSystemId(new File(filename).toURI().toString());
                DocumentBuilderFactory dfactory = DocumentBuilderFactory.newInstance();
                dfactory.setNamespaceAware(true);
                document = dfactory.newDocumentBuilder().parse(in);

            } else if (objectModel.equals(NamespaceConstant.OBJECT_MODEL_JDOM)) {
                InputSource in = new InputSource(new FileInputStream(filename));
                in.setSystemId(new File(filename).toURI().toString());
                SAXBuilder builder = new SAXBuilder();
                document = builder.build(in);

            } else if (objectModel.equals(NamespaceConstant.OBJECT_MODEL_DOM4J)) {
                org.dom4j.io.SAXReader parser = new org.dom4j.io.SAXReader();
                document = parser.read(new File(filename));

            } else if (objectModel.equals(NamespaceConstant.OBJECT_MODEL_XOM)) {
                nu.xom.Builder builder = new nu.xom.Builder();
                document = builder.build(new File(filename));
            }

            // Use the JAXP 1.3 XPath API to apply the xpath expression to the doc.
            System.out.println("Querying " + om + " using " + xpathExpressionStr);


            // Declare a namespace context:
            xpath.setNamespaceContext(
                    new NamespaceContext() {
                        public String getNamespaceURI(String s) {
                            if (s.equals("f")) {
                                return "http://localhost/f";
                            } else {
                                return null;
                            }
                        }

                        public String getPrefix(String s) { return null; }

                        public Iterator getPrefixes(String s) { return null; }
                    }
                );

            // Declare a variable:

            final QName f_var = new QName("http://localhost/f", "pi");
            xpath.setXPathVariableResolver(
                    new XPathVariableResolver() {
                        public Object resolveVariable(QName qName) {
                            if (qName.equals(f_var)) {
                                return new Double(Math.PI);
                            } else {
                                return null;
                            }
                        }
                    }
                );

            // Declare a function:

            final XPathFunction sqrt = new XPathFunction() {
                public Object evaluate(List list) throws XPathFunctionException {
                    Object arg = list.get(0);
                    if (!(arg instanceof Double)) {
                        throw new XPathFunctionException("f:sqrt() expects an xs:double argument");
                    }
                    return new Double(Math.sqrt(((Double)arg).doubleValue()));
                }
            };

            final QName f_sqrt = new QName("http://localhost/f", "sqrt");
            xpath.setXPathFunctionResolver(
                    new XPathFunctionResolver() {
                        public XPathFunction resolveFunction(QName qName, int arity) {
                            if (qName.equals(f_sqrt) && arity==1) {
                                return sqrt;
                            } else {
                                return null;
                            }
                        }
                    }
                );


            // Now compile the expression
            XPathExpression xpathExpression = xpath.compile(xpathExpressionStr);


            // Now evaluate the expression on the document to get String result
            String resultString = xpathExpression.evaluate(document);

            // Serialize the found nodes to System.out.
            System.out.println("<output>");
            System.out.println("String Value => " + resultString);
            System.out.println("</output>");
        } else {
            System.out.println("Bad input args: " + filename + ", " + xpathExpressionStr);
        }
    }


    /**
     * Main method to run from the command line.
     */
    public static void main(String[] args)
            throws Exception {
        if (args.length != 2 && args.length != 3) {
            System.out.println("java ApplyXPathJAXP filename.xml xpath [saxon|dom|jdom|xom]\n"
                    + "Reads filename.xml and applies the xpath; prints the String value of result.");
            return;
        }

        ApplyXPathJAXP app = new ApplyXPathJAXP();
        app.doMain(args);
    }

} // end of class ApplyXPathJAXP

