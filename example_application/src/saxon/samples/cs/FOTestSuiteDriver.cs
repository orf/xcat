using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Saxon.Api;
using System.Xml;
using System.IO;
using System.Text.RegularExpressions;
using JFeatureKeys=net.sf.saxon.lib.FeatureKeys;
using JNamespaceConstant=net.sf.saxon.lib.NamespaceConstant;
using JStandardModuleURIResolver=net.sf.saxon.lib.StandardModuleURIResolver;
using TestRunner;
using System.Globalization;



    /**
     * Test Driver for the Functions and Operators test suite
     */
    public class FOTestSuiteDriver
    {

        static void MainXXX(string[] args)
        {
            if (args.Length == 0 || args[0].Equals("-?"))
            {
                Console.WriteLine("FOTestSuiteDriver testsuiteDir resultsDir testName?");
            }
            try
            {
                new FOTestSuiteDriver().go(args);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Console.WriteLine(e.StackTrace);
            }
        }


        public static string RNS = "http://www.w3.org/2010/09/qt-fots-catalog";

        String testSuiteDir;
        Processor driverProc = new Processor(true);
        Serializer driverSerializer = new Serializer();
        Dictionary<string, TestEnvironment> globalEnvironments = new Dictionary<string, TestEnvironment>();
        Dictionary<string, TestEnvironment> localEnvironments = new Dictionary<string, TestEnvironment>();
        Regex testPattern = null;
        string testFuncSet = null;
        string resultsDir = null;
        private bool debug = false;
        StreamWriter results;
        private int successes = 0;
        private int failures = 0;
        private int wrongErrorResults = 0;
        private bool unfolded = false;
        private int generateByteCode = 0;
        private bool preferQuery = false;
        private TreeModel treeModel = TreeModel.TinyTree;
        private Dictionary<string, XdmNode> exceptionsMap = new Dictionary<string, XdmNode>();
        IFeedbackListener feedback;
        


        /*public static void main(string[] args) throws Exception {
            if (args.length == 0 || args[0].Equals("-?")) {
                Console.WriteLine("java com.saxonica.testdriver.FOTestSuiteDriver catalog [-o:resultsdir] [-s:testSetName]" +
                        " [-t:testNamePattern] [-unfolded] [-bytecode:on|off|debug] [-xquery] [-tree]");
            }

            Console.WriteLine("Testing Saxon " + Version.getProductVersion());
            new FOTestSuiteDriver().go(args);
        }*/

        /**
         * An environment captures the content of an &lt;environment&gt; element in the catalog: a named set
         * of source documents, schemas, etc
         */

        public class TestEnvironment
        {
            public Processor processor;
            public Dictionary<string, XdmNode> sourceDocs;
            public XPathCompiler xpathCompiler;
            public XQueryCompiler xqueryCompiler;
            public XdmNode contextNode;
            public Dictionary<QName, XdmValue> params1 = new Dictionary<QName, XdmValue>();
            public bool xml11 = false;
            public bool usable = true;
            public StringBuilder paramDeclarations = new StringBuilder(256);
            public StringBuilder paramDecimalDeclarations = new StringBuilder(256);
        }

        /**
         * The outcome of a test is either an XDM value or an exception.
         */

        private class Outcome
        {
            private XdmValue value;
            private Hashtable errorsReported;
            private DynamicError exception; /*SaxonApiException*/
            private StaticError staticException;

            public Outcome(XdmValue value)
            {
                this.value = value;
            }

            public Outcome(DynamicError exception)
            {
                this.exception = exception;
            }

            public Outcome(StaticError exception)
            {
                this.staticException = exception;
            }

            public bool isException()
            {
                return exception != null || staticException != null;
            }

            public Exception getException()
            {
                if (exception != null)
                {
                    return exception;
                }else {
                    return staticException;
                }
            }

            public XdmValue getResult()
            {
                return value;
            }

            public void setErrorsReported(Hashtable errors)
            {
                errorsReported = errors;
            }

            public bool hasReportedError(string errorCode)
            {
                return errorsReported != null && errorsReported.Contains(errorCode);
            }

            public string ToString()
            {
                return (isException() ? "EXCEPTION " + exception.Message : value.ToString());
            }

            public string serialize(Processor p)
            {
                if (isException())
                {
                    return "EXCEPTION " + exception.Message;
                }
                else
                {
                    StringWriter sw = new StringWriter();
                    Serializer s = new Serializer();
                    s.SetOutputWriter(sw);
                    s.SetOutputProperty(Serializer.METHOD, "xml");
                    s.SetOutputProperty(Serializer.INDENT, "yes");
                    s.SetOutputProperty(Serializer.OMIT_XML_DECLARATION, "yes");
                    try
                    {

                        (new Processor()).WriteXdmValue(value, s);                       
                    }
                    catch (DynamicError err)
                    {
                        return ("SERIALIZATION FAILED: " + err.Message);
                    }
                    return sw.ToString();
                }
            }
        }

        public void setFeedbackListener(IFeedbackListener f)
        {
            feedback = f;
        }

        public void go(string[] args)
        {
            testSuiteDir = args[0];
            if (testSuiteDir.EndsWith("/"))
            {
                testSuiteDir = testSuiteDir.Substring(0, testSuiteDir.Length - 1);
            }

            resultsDir = args[1];
            if (resultsDir.EndsWith("/"))
            {
                resultsDir = resultsDir.Substring(0, resultsDir.Length - 1);
            }

            string catalog = testSuiteDir + "\\catalog.xml";

            Hashtable exceptions = new Hashtable();

            for (int i = 1; i < args.Length; i++)
            {
                if (args[i].StartsWith("-t:"))
                {
                    testPattern = new Regex(args[i].Substring(3));
                }
                if (args[i].StartsWith("-s:"))
                {
                    testFuncSet = args[i].Substring(3);
                }
                if (args[i].StartsWith("-o"))
                {
                    resultsDir = args[i].Substring(3);
                }
                if (args[i].StartsWith("-debug"))
                {
                    debug = true;
                }
                if (args[i].Equals("-unfolded"))
                {
                    unfolded = true;
                }
                if (args[i].StartsWith("-bytecode"))
                {
                    if (args[i].Substring(10).Equals("on"))
                    {
                        generateByteCode = 1;
                    }
                    else if (args[i].Substring(10).Equals("debug"))
                    {
                        generateByteCode = 2;
                    }
                    else
                    {
                        generateByteCode = 0;
                    }
                }
                if (args[i].StartsWith("-xquery"))
                {
                    preferQuery = true;
                }
                /*if (args[i].StartsWith("-tree")) {
                    if (args[i].Substring(6).Equals("jdom") || args[i].Substring(6).Equals("JDOM")) {
                        treeModel = new JDOMObjectModel();
                    } else if (args[i].Substring(6).Equals("jdom2") || args[i].Substring(6).Equals("JDOM2")) {
                        treeModel = new JDOM2ObjectModel();
                    } else if (args[i].Substring(6).Equals("tinytree") || args[i].Substring(6).Equals("TINYTREE")) {
                        treeModel = TreeModel.TinyTree;
                    }else {
                        throw new Exception("The TreeModel specified does not exist");
                    }
                } */
            }
            if (resultsDir == null)
            {
                Console.WriteLine("No results directory specified (use -o:dirname)");
                System.Environment.Exit(2);
            }

            //driverSerializer.SetOutputStream(Console.Error);
            // driverSerializer.SetOutputProperty(Serializer.OMIT_XML_DECLARATION, "yes");

            processCatalog(catalog);
            Console.WriteLine(successes + " successes, " + failures + " failures, " + wrongErrorResults + " incorrect ErrorCode");
            feedback.Message(successes + " successes, " + failures + " failures, " + wrongErrorResults + " incorrect ErrorCode"+ Environment.NewLine, false);
        }

        public void processCatalog(string catalogFile)
        {
            DocumentBuilder builder = driverProc.NewDocumentBuilder();
            XdmNode catalog = builder.Build(new Uri(catalogFile));
            DocumentBuilder catbuilder = driverProc.NewDocumentBuilder();
            //catbuilder.SetTreeModel(treeModel);
            XPathCompiler xpc = driverProc.NewXPathCompiler();
            xpc.BaseUri = "";// catalogFile;
            xpc.XPathLanguageVersion = "3.0";
            xpc.Caching = true;
            xpc.DeclareNamespace("", "http://www.w3.org/2010/09/qt-fots-catalog");
            IEnumerator en = xpc.Evaluate("//environment", catalog).GetEnumerator();
            while (en.MoveNext())
            {
                XdmNode envi = (XdmNode)en.Current;
                processEnvironment(xpc, envi, globalEnvironments);
            }

            try
            {
                WriteResultFilePreamble(driverProc, catalog, DateTime.Today.ToString());
            }
            catch (Exception e)
            {
                feedback.Message(e.StackTrace, false);
            }

            /**
             * Look for an exceptions.xml document with the general format:
             *
             * <exceptions xmlns="...test catalog namespace...">
             *   <exception test-set ="testset1" test-case="testcase" run="yes/no/not-unfolded"
             *       bug="bug-reference" reason="">
             *     <results>
             *         ... alternative expected results ...
             *     </results>
             *     <optimization>
             *         ... assertions about the "explain" tree
             *     </optimization>
             *   </exception>
             * </exceptions>
             *
             */
            XdmNode exceptionsDoc = null;
            DocumentBuilder exceptBuilder = driverProc.NewDocumentBuilder();
            QName testCase = new QName("", "test-case");
            try
            {
                exceptionsDoc = exceptBuilder.Build(new Uri(resultsDir + "/exceptions.xml"));
                //XdmSequenceIterator iter
                IEnumerator iter = exceptionsDoc.EnumerateAxis(XdmAxis.Descendant, new QName(RNS, "exception"));
                while (iter.MoveNext())
                {
                    XdmNode entry = (XdmNode)iter.Current;
                    string test = entry.GetAttributeValue(testCase);
                    if (test != null)
                    {
                        exceptionsMap.Add(test, entry);
                    }
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("*** Failed to process exceptions file: " + e.Message);
            }

            if (testFuncSet != null)
            {
                try
                {
                    XdmNode funcSetNode = (XdmNode)xpc.EvaluateSingle("//test-set[@name='" + testFuncSet + "']", catalog);
                    if (funcSetNode == null)
                    {
                        throw new Exception("Test-set " + testFuncSet + " not found!");
                    }
                    processTestSet(catbuilder, xpc, funcSetNode);
                }
                catch (Exception e1)
                {
                    //   e1.printStackTrace();
                }
            }
            else
            {
                en = xpc.Evaluate("//test-set", catalog).GetEnumerator();
                while (en.MoveNext())
                {
                    processTestSet(catbuilder, xpc, ((XdmNode)en.Current));
                }
            }
            try
            {
              writeResultFilePostamble();
            }
            catch (Exception e)
            {
                //  e.printStackTrace();
            }


        }

        private void processTestSet(DocumentBuilder catbuilder, XPathCompiler xpc, XdmNode funcSetNode)
        {
            string testName;
            try
            {
                results.WriteLine("<test-set name='" + funcSetNode.GetAttributeValue(new QName("name")) + "'>");
            }
            catch (Exception e)
            {
            }
            string testSetFile = testSuiteDir + "\\" + funcSetNode.GetAttributeValue(new QName("file"));
            xpc.BaseUri = testSetFile;
            XdmNode testSetDocNode = catbuilder.Build(new Uri(testSetFile));
            localEnvironments.Clear();
            TestEnvironment defaultEnvironment = createLocalEnvironment(testSetDocNode.BaseUri);
            localEnvironments.Add("default", defaultEnvironment);
            bool run = true;
            IEnumerator dependency = xpc.Evaluate("/test-set/dependency", testSetDocNode).GetEnumerator();
            while (dependency.MoveNext())
            {
                if (!DependencyIsSatisfied((XdmNode)dependency.Current, defaultEnvironment))
                {
                    run = false;
                }
            }
            if (run)
            {
                IEnumerator iter = xpc.Evaluate("//environment[@name]", testSetDocNode).GetEnumerator();
                while (iter.MoveNext())
                {
                    processEnvironment(xpc, (XdmNode)iter.Current, localEnvironments);
                }
                IEnumerator testCases = xpc.Evaluate("//test-case", testSetDocNode).GetEnumerator();
                while (testCases.MoveNext())
                {
                    testName = ((XdmNode)xpc.EvaluateSingle("@name", (XdmItem)testCases.Current)).StringValue;
                    if (testPattern != null && !testPattern.Match(testName).Success)
                    {
                        continue;
                    }
                    feedback.Message("Test set " + funcSetNode.GetAttributeValue(new QName("name")) + " ", false);
                    runTestCase((XdmNode)testCases.Current, xpc);
                }
            }
            try
            {
                results.WriteLine("</test-set>");
            }
            catch (Exception e)
            {
            }
        }

        /**
         * Construct a local default environment for a test set
         */

        private TestEnvironment createLocalEnvironment(Uri baseUri)
        {
            TestEnvironment environment = new TestEnvironment();
            environment.processor = new Processor(true);
            //activate(environment.processor);
            if (generateByteCode == 1)
            {
                environment.processor.SetProperty("http://saxon.sf.net/feature/generateByteCode", "true");
                environment.processor.SetProperty("http://saxon.sf.net/feature/debugByteCode", "false");
            }
            else if (generateByteCode == 2)
            {
                environment.processor.SetProperty("http://saxon.sf.net/feature/generateByteCode", "true");
                environment.processor.SetProperty("http://saxon.sf.net/feature/debugByteCode", "true");
            }
            else
            {
                environment.processor.SetProperty("http://saxon.sf.net/feature/generateByteCode", "false");
                environment.processor.SetProperty("http://saxon.sf.net/feature/debugByteCode", "false");
            }
            environment.xpathCompiler = environment.processor.NewXPathCompiler();
            environment.xpathCompiler.BaseUri = baseUri.ToString();
            environment.xqueryCompiler = environment.processor.NewXQueryCompiler();
            environment.xqueryCompiler.BaseUri = baseUri.ToString();
            if (unfolded)
            {
                //TODO  environment.xqueryCompiler.getUnderlyingStaticContext().setCodeInjector(new LazyLiteralInjector());
            }
            //environment.processor.getUnderlyingConfiguration().setDefaultCollection(null);
            return environment;
        }

        /**
         * Construct an Environment
         *
         * @param xpc          the XPathCompiler used to process the catalog file
         * @param env          the Environment element in the catalog file
         * @param environments the set of environments to which this one should be added (may be null)
         * @return the constructed Environment object
         * @throws SaxonApiException
         */

        private TestEnvironment processEnvironment(XPathCompiler xpc, XdmItem env, Dictionary<string, TestEnvironment> environments)
        {
            TestEnvironment environment = new TestEnvironment();
            string name = ((XdmNode)env).GetAttributeValue(new QName("name"));
            environment.processor = new Processor(true);
            XmlUrlResolver res = new XmlUrlResolver();
            if (generateByteCode == 1)
            {
                environment.processor.SetProperty(JFeatureKeys.GENERATE_BYTE_CODE, "true");
                environment.processor.SetProperty(JFeatureKeys.DEBUG_BYTE_CODE, "false");
            }
            else if (generateByteCode == 2)
            {
                environment.processor.SetProperty(JFeatureKeys.GENERATE_BYTE_CODE, "true");
                environment.processor.SetProperty(JFeatureKeys.DEBUG_BYTE_CODE, "true");
            }
            else
            {
                environment.processor.SetProperty(JFeatureKeys.GENERATE_BYTE_CODE, "false");
                environment.processor.SetProperty(JFeatureKeys.DEBUG_BYTE_CODE, "false");
            }
            environment.xpathCompiler = environment.processor.NewXPathCompiler();
            environment.xpathCompiler.BaseUri = (((XdmNode)env).BaseUri).ToString();
            environment.xqueryCompiler = environment.processor.NewXQueryCompiler();
            environment.xqueryCompiler.BaseUri = (((XdmNode)env).BaseUri).ToString();
            if (unfolded)
            {
                //environment.xqueryCompiler.getUnderlyingStaticContext().setCodeInjector(new LazyLiteralInjector());
            }
            DocumentBuilder builder = environment.processor.NewDocumentBuilder();
            environment.sourceDocs = new Dictionary<string, XdmNode>();
            if (environments != null && name != null)
            {
                try
                {
                    environments.Add(name, environment);
                }catch(Exception e){}
            }
            System.Collections.IEnumerator dependency = xpc.Evaluate("dependency", env).GetEnumerator();

            while (dependency.MoveNext())
            {
                if (!DependencyIsSatisfied((XdmNode)dependency.Current, environment))
                {
                    environment.usable = false;
                }
            }

            // set the base Uri if specified
            IEnumerator base1 = xpc.Evaluate("static-base-uri", env).GetEnumerator();
            while (base1.MoveNext())
            {
                string Uri = ((XdmNode)base1.Current).GetAttributeValue(new QName("uri"));
                try
                {
                    environment.xpathCompiler.BaseUri = Uri;
                    environment.xqueryCompiler.BaseUri = Uri;
                }
                catch (Exception e)
                {
                    Console.WriteLine("**** invalid base Uri " + Uri);
                }
            }
            // set any requested collations
            base1 = xpc.Evaluate("collation", env).GetEnumerator();
            while (base1.MoveNext())
            {
                string uriStr = ((XdmNode)base1.Current).GetAttributeValue(new QName("uri"));
                string defaultAtt = ((XdmNode)base1.Current).GetAttributeValue(new QName("default"));
                Boolean defaultCol = false;
                if (defaultAtt != null && (defaultAtt.Trim().Equals("true") || defaultAtt.Trim().Equals("1")))
                {
                    defaultCol = true;
                }
                if (uriStr.Equals("http://www.w3.org/2010/09/qt-fots-catalog/collation/caseblind"))
                {
                    net.sf.saxon.Configuration config = xpc.Processor.Implementation;
                    net.sf.saxon.lib.StringCollator collator = config.getCollationURIResolver().resolve("http://saxon.sf.net/collation?ignore-case=yes", "", config);

                    CompareInfo compareInfo = CultureInfo.CurrentCulture.CompareInfo;
                    CompareOptions options = CompareOptions.IgnoreCase;

                    environment.xpathCompiler.DeclareCollation(new Uri(uriStr), compareInfo, options, defaultCol);
                    environment.xqueryCompiler.DeclareCollation(new Uri(uriStr), compareInfo, options, defaultCol);
                }
               
            }

            // declare the requested namespaces
            IEnumerator nsElement = xpc.Evaluate("namespace", env).GetEnumerator();
            while (nsElement.MoveNext())
            {
                string prefix = ((XdmNode)nsElement.Current).GetAttributeValue(new QName("prefix"));
                string uri = ((XdmNode)nsElement.Current).GetAttributeValue(new QName("uri"));
                environment.xpathCompiler.DeclareNamespace(prefix, uri);
                environment.xqueryCompiler.DeclareNamespace(prefix, uri);
            }

            // load the requested schema documents
            SchemaManager manager = environment.processor.SchemaManager;
            System.Collections.IEnumerator schema = xpc.Evaluate("schema", env).GetEnumerator();
            while (schema.MoveNext())
            {
                string href = ((XdmNode)schema.Current).GetAttributeValue(new QName("file"));
                manager.Compile((new Uri(((XdmNode)env).BaseUri, href)));
            }

            // load the requested source documents
            //IEnumerator source = xpc.Evaluate("source", env).GetEnumerator();
            foreach (XdmItem source in xpc.Evaluate("source", env))
            {
                Uri href = res.ResolveUri(((XdmNode)env).BaseUri, ((XdmNode)source).GetAttributeValue(new QName("file")));
                string Uri = ((XdmNode)source).GetAttributeValue(new QName("uri"));
                string validation = ((XdmNode)source).GetAttributeValue(new QName("", "validation"));
                XdmNode doc = null;
                
                if (validation == null || validation.Equals("skip"))
                {
                    try
                    {
                        doc = builder.Build(href);
                       
                    }
                    catch (Exception e)
                    {
                        feedback.Message("Error:" + e.Message+" *** failed to build source document " + href, false);
                    }
                }
                else
                {
                    try
                    {
                        SchemaValidator validator = manager.NewSchemaValidator();
                        XdmDestination xdmDest = new XdmDestination();
                        validator.IsLax = validation.Equals("lax");
                        validator.SetDestination(xdmDest);
                        validator.SetSource(href);
                        validator.Run();
                        doc = xdmDest.XdmNode;
                        environment.xpathCompiler.SchemaAware = true;
                        environment.xqueryCompiler.SchemaAware = true;
                    }
                    catch(Exception e) {
                        feedback.Message("Error:" + e.Message+" *** failed to build source document " + href, false);
                    }

                }

                if (Uri != null)
                {
                    environment.sourceDocs.Add(Uri, doc);
                }
                string role = ((XdmNode)source).GetAttributeValue(new QName("role"));
                if (role != null)
                {
                    if (".".Equals(role))
                    {
                        environment.contextNode = doc;
                    }
                    else if (role.StartsWith("$"))
                    {
                        string varName = role.Substring(1);
                        environment.params1.Add(new QName(varName), doc);
                        environment.xpathCompiler.DeclareVariable(new QName(varName));
                        environment.paramDeclarations.Append("declare variable $" + varName + " external; ");
                    }
                }
              
            }

            // create a collection Uri resolved to handle the requested collections
            Hashtable collections = new Hashtable();
          

            foreach (XdmItem coll in xpc.Evaluate("collection", env))
            {
                string collectionUri = ((XdmNode)coll).GetAttributeValue(new QName("uri"));
                if (collectionUri == null || collectionUri.Equals(""))
                {
                    collectionUri = "http://www.saxonica.com/defaultCollection";
                }

                IList<Uri> docs = new List<Uri>();
                
                foreach (XdmItem source in xpc.Evaluate("source", coll))
                {
                   

                    Uri href = res.ResolveUri(((XdmNode)env).BaseUri, ((XdmNode)source).GetAttributeValue(new QName("file")));
                    //File file = new File((((XdmNode) env).GetBaseUri().resolve(href)));
                    string id = ((XdmNode)source).GetAttributeValue(new QName(JNamespaceConstant.XML, "id"));
                    XdmNode doc = builder.Build(href);
                    if (id != null)
                    {
                        environment.sourceDocs.Add(id, doc);
                    }
                    
                    environment.processor.RegisterCollection(href, getCollection(doc, href.AbsoluteUri));
                    environment.sourceDocs.Add(href.ToString(), doc);
                     docs.Add(doc.DocumentUri);
                }
                try {
                    collections.Add(new Uri(collectionUri), docs);
                } catch (Exception e) {
                    feedback.Message("**** Invalid collection Uri " + collectionUri, false);
                }

            }
            if (collections.Count != 0) {
                environment.processor.Implementation.setCollectionURIResolver(new CollectionResolver(collections));
               /*     new net.sf.saxon.lib.CollectionURIResolver() {
                            public SequenceIterator resolve(string href, string base, XPathContext context)  {
                                try {
                                    List<AnyUriValue> docs;
                                    if (href == null) {
                                        docs = collections.get(new Uri(""));
                                    } else {
                                        Uri abs = new Uri(base).resolve(href);
                                        docs = collections.get(abs);
                                    }
                                    if (docs == null) {
                                        return EmptyIterator.getInstance();
                                    } else {
                                        return new ListIterator(docs);
                                    }
                                } catch (UriSyntaxException e) {
                                    Console.WriteLine("** Invalid Uri: " + e.Message);
                                    return EmptyIterator.getInstance();
                                }
                            }
                        }
                )*/
            }

            // register any required decimal formats
            IEnumerator decimalFormat = xpc.Evaluate("decimal-format", env).GetEnumerator();
            while (decimalFormat.MoveNext())
            {

                   XdmNode formatElement = (XdmNode) decimalFormat.Current;
                   string formatName = formatElement.GetAttributeValue(new QName("name"));
                   QName formatQName = null;
                   if (formatName != null) {
                       if (formatName.IndexOf(':') < 0) {
                           formatQName = new QName("", "", formatName);
                       } else {
                           try {
                               formatQName =  new QName(environment.xpathCompiler.GetNamespaceURI(formatName, false), formatName.Substring(formatName.IndexOf(':')+1));
                           } catch (Exception) {
                               feedback.Message("**** Invalid QName as decimal-format name", false);
                               formatQName = new QName("", "", "error-name");
                           }
                       }
                       environment.paramDecimalDeclarations.Append("declare decimal-format " + formatName + " ");
                   } else {
                       environment.paramDecimalDeclarations.Append("declare default decimal-format ");
                   }
                   foreach (XdmItem decimalFormatAtt in xpc.Evaluate("@* except @name", formatElement)) {
                       XdmNode formatAttribute = (XdmNode) decimalFormatAtt;
                       string property = formatAttribute.NodeName.LocalName;
                       string value = formatAttribute.StringValue;
                       environment.paramDecimalDeclarations.Append(property + "=\"" + value + "\" ");
                       environment.xpathCompiler.SetDecimalFormatProperty(formatQName, property, value);
                      
                   }
                   environment.paramDecimalDeclarations.Append(";");
            }

            // declare any variables
            IEnumerator param = xpc.Evaluate("param", env).GetEnumerator();
            while (param.MoveNext())
            {
                string varName = ((XdmNode)param.Current).GetAttributeValue(new QName("name"));
                XdmValue value = null;
                string sourceStr = ((XdmNode)param.Current).GetAttributeValue(new QName("source"));
                if (sourceStr != null)
                {
                    XdmNode sourceDoc = (XdmNode)(environment.sourceDocs[sourceStr]);
                    if (sourceDoc == null)
                    {
                        Console.WriteLine("**** Unknown source document " + sourceDoc.ToString());
                    }
                    value = sourceDoc;
                }
                else
                {
                    string select = ((XdmNode)param.Current).GetAttributeValue(new QName("select"));
                    value = xpc.Evaluate(select, null);
                }
                environment.params1.Add(new QName(varName), value);
                environment.xpathCompiler.DeclareVariable(new QName(varName));
                string declared = ((XdmNode)param.Current).GetAttributeValue(new QName("declared"));
                if (declared != null && "true".Equals(declared) || "1".Equals(declared))
                {
                    // no action
                }
                else
                {
                    environment.paramDeclarations.Append("declare variable $" + varName + " external; ");
                }
            }

            return environment;
        }

        public class CollectionResolver: net.sf.saxon.lib.CollectionURIResolver {
            Hashtable collections;
            public CollectionResolver(Hashtable collections)
            { 
                this.collections = collections;
            }
                            public net.sf.saxon.om.SequenceIterator resolve(string href, string baseStr, net.sf.saxon.expr.XPathContext context)  {
                                try {
                                    List<Uri> docs;
                                    if (href == null) {
                                        docs = (List<Uri>)collections[new Uri("http://www.saxonica.com/defaultCollection")];
                                    } else {
                                        XmlUrlResolver res = new XmlUrlResolver();
                                        Uri abs= res.ResolveUri(new Uri(baseStr), href);
                                        docs = (List<Uri>)collections[abs];
                                    }
                                    if (docs == null) {
                                        return net.sf.saxon.tree.iter.EmptyIterator.getInstance();
                                    } else {
                                        java.util.List list = new java.util.ArrayList();
                                        foreach(Uri uri in docs){
                                            list.add(new net.sf.saxon.value.AnyURIValue(uri.ToString()));
                                        }
                                        
                                        return new net.sf.saxon.tree.iter.ListIterator(list);
                                    }
                                } catch (java.net.URISyntaxException e) {
                                    Console.WriteLine("** Invalid Uri: " + e.Message);
                                    return net.sf.saxon.tree.iter.EmptyIterator.getInstance();
                                }
                            }
                        }

        private IList getCollection(XdmNode collectionNode, string href)
        {
            ArrayList list = new ArrayList(10);
            IEnumerator e = collectionNode.EnumerateAxis(
                XdmAxis.Child, new QName("input-document"));
            while (e.MoveNext())
            {
                XdmNode node = (XdmNode)e.Current;
                list.Add(new Uri(href));
            }
            return list;
        }

        /**
         * Get the Unicode codepoint corresponding to a string, which must represent a single Unicode character
         *
         * @param s the input string, representing a single Unicode character, perhaps as a surrogate pair
         * @return
         * @throws net.sf.saxon.trans.XPathException
         *
         */
        private int toChar(string s)
        {
            /*TODO int[] e = StringValue.expand(s);
            if (e.length != 1) {
                Console.WriteLine("Attribute \"" + s + "\" should be a single character");
            }
            return e[0];*/
            return 0;
        }

        /**
         * Decide whether a dependency is satisfied
         *
         * @param dependency the dependency element in the catalog
         * @param env        an environment in the catalog, which can be modified to satisfy the dependency if necessary.
         *                   May be null.
         * @return true if the environment satisfies the dependency, else false
         */

        private bool DependencyIsSatisfied(XdmNode dependency, TestEnvironment env)
        {
            string type = dependency.GetAttributeValue(new QName("type"));
            string value = dependency.GetAttributeValue(new QName("value"));
            bool inverse = "false".Equals(dependency.GetAttributeValue(new QName("satisfied")));
            if ("xml-version".Equals(type))
            {
                if ("1.1".Equals(value) && !inverse)
                {
                    if (env != null)
                    {
                        env.processor.XmlVersion = (decimal)1.1;
                    }
                    else
                    {
                        return false;
                    }
                }
                return true;
            }
            else if ("xsd-version".Equals(type))
            {
                if ("1.1".Equals(value))
                {
                    if (env != null)
                    {

                        env.processor.SetProperty(JFeatureKeys.XSD_VERSION, (inverse ? "1.0" : "1.1"));
                    }
                    else
                    {
                        return false;
                    }
                }
                else if ("1.0".Equals(value))
                {
                    if (env != null)
                    {
                        env.processor.SetProperty(JFeatureKeys.XSD_VERSION, (inverse ? "1.1" : "1.0"));
                    }
                    else
                    {
                        return false;
                    }
                }
                return true;
            }
            else if ("limits".Equals(type))
            {
                if ("year_lt_0".Equals(value) && !inverse)
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }
            else if ("spec".Equals(type))
            {
                return true;
            }
            else if ("collection-stability".Equals(type))
            {
                // SAXON has a problem here - we don't support stable collections
                return ("false".Equals(value) != inverse);
            }
            else if ("default-language".Equals(type))
            {
                return ("en".Equals(value) != inverse);
            }
            else if ("directory-as-collection-Uri".Equals(type))
            {
                return ("true".Equals(value) != inverse);
            }
            else if ("language".Equals(type))
            {
                return (("en".Equals(value) || "de".Equals(value) || "fr".Equals(value)) != inverse);
            }
            else if ("calendar".Equals(type))
            {
                return (("AD".Equals(value) || "ISO".Equals(value)) != inverse);
            }
            else if ("format-integer-sequence".Equals(type))
            {
                return !inverse;
            }
            else if ("feature".Equals(type))
            {
                if ("namespace-axis".Equals(value))
                {
                    return !inverse;
                }
                else if ("schemaImport".Equals(value) || "schemaValidation".Equals(value))
                {
                    // Need to reset these after use for this query??
                    if (env != null)
                    {
                        env.xpathCompiler.SchemaAware  = true;
                        env.xqueryCompiler.SchemaAware = true;
                    }
                    return true;
                }
                else if ("xpath-1.0-compatibility".Equals(value))
                {
                    if (env != null)
                    {
                        env.xpathCompiler.BackwardsCompatible = !inverse;
                        return true;
                    }
                    else
                    {
                        return false;
                    }
                }
                else if ("schema-location-hint".Equals(value))
                {
                    return !inverse;
                }
                else
                {
                    Console.WriteLine("**** feature = " + value + "  ????");
                    return false;
                }
            }
            else
            {
                Console.WriteLine("**** dependency not recognized: " + type);
                return false;
            }
        }

        /**
         * Run a test case
         *
         * @param testCase the test case element in the catalog
         * @param xpc      the XPath compiler to be used for compiling XPath expressions against the catalog
         * @throws SaxonApiException
         */

        private void runTestCase(XdmNode testCase, XPathCompiler xpc)
        {
            string testCaseName = testCase.GetAttributeValue(new QName("name"));
            feedback.Message("Test case " + testCaseName + Environment.NewLine, false);

            XdmNode exceptionElement = null;
            try
            {
                exceptionElement = exceptionsMap[testCaseName];
            }
            catch (Exception) { }

            XdmNode alternativeResult = null;
            XdmNode optimization = null;
            if (exceptionElement != null)
            {
                string runAtt = exceptionElement.GetAttributeValue(new QName("run"));
                if ("no".Equals(runAtt))
                {
                    WriteTestCaseElement(testCaseName, "notRun", "see exceptions file");
                    return;
                }
                if (unfolded && "not-unfolded".Equals(runAtt))
                {
                    WriteTestCaseElement(testCaseName, "notRun", "see exceptions file");
                    return;
                }

                alternativeResult = (XdmNode)xpc.EvaluateSingle("result", exceptionElement);
                optimization = (XdmNode)xpc.EvaluateSingle("optimization", exceptionElement);
            }

            XdmNode environmentNode = (XdmNode)xpc.EvaluateSingle("environment", testCase);
            TestEnvironment env = null;
            if (environmentNode == null)
            {
                env = localEnvironments["default"];
            }
            else
            {
                string envName = environmentNode.GetAttributeValue(new QName("ref"));
                if (envName == null)
                {
                    env = processEnvironment(xpc, environmentNode, null);
                }
                else
                {
                    try
                    {
                        env = localEnvironments[envName];
                    }
                    catch (Exception) { }
                    if (env == null)
                    {
                        try
                        {
                            env = globalEnvironments[envName];
                        }
                        catch (Exception) { }
                    }
                    if (env == null)
                    {
                        Console.WriteLine("*** Unknown environment " + envName);
                        WriteTestCaseElement(testCaseName, "fail", "Environment " + envName + " not found");
                        failures++;
                        return;
                    }
                }
            }
            env.xpathCompiler.BackwardsCompatible = false;
            env.processor.XmlVersion = (decimal)1.0;

            bool run = true;
            bool xpDependency = false;
            string hostLang;
            string langVersion;
            if (preferQuery)
            {
                hostLang = "XQ";
                langVersion = "1.0";
            }
            else
            {
                hostLang = "XP";
                langVersion = "2.0";
            }
            XdmValue dependencies = xpc.Evaluate("/*/dependency, ./dependency", testCase);
            foreach (XdmItem dependency in dependencies)
            {
                string type = ((XdmNode)dependency).GetAttributeValue(new QName("type"));
                if (type == null)
                {
                    throw new Exception("dependency/@type is missing");
                }
                string value = ((XdmNode)dependency).GetAttributeValue(new QName("value"));
                if (value == null)
                {
                    throw new Exception("dependency/@value is missing");
                }
                if (type.Equals("spec"))
                {
                    if (value.Contains("XP") && !value.Contains("XQ"))
                    {
                        hostLang = "XP";
                        langVersion = (value.Equals("XP20") ? "2.0" : "3.0");
                        xpDependency = true;
                    }
                    else if (value.Contains("XP") && value.Contains("XQ") && preferQuery)
                    {
                        hostLang = "XQ";
                        langVersion = (value.Contains("XQ10+") || value.Contains("XQ30") ? "3.0" : "1.0");
                    }
                    else if (value.Contains("XT"))
                    {
                        hostLang = "XT";
                        langVersion = (value.Contains("XT30+") || value.Contains("XT30") ? "3.0" : "1.0");
                    }
                    else
                    {
                        hostLang = "XQ";
                        langVersion = (value.Contains("XQ10+") || value.Contains("XQ30") ? "3.0" : "1.0");
                    }
                }
                if (type.Equals("feature") && value.Equals("xpath-1.0-compatibility"))
                {
                    hostLang = "XP";
                    langVersion = "3.0";
                    xpDependency = true;
                }
                if (type.Equals("feature") && value.Equals("namespace-axis"))
                {
                    hostLang = "XP";
                    langVersion = "3.0";
                    xpDependency = true;
                }

                if (!DependencyIsSatisfied((XdmNode)dependency, env))
                {
                    Console.WriteLine("*** Dependency not satisfied: " + ((XdmNode)dependency).GetAttributeValue(new QName("type")));
                    WriteTestCaseElement(testCaseName, "notRun", "Dependency not satisfied");
                    run = false;
                }
            }
            if ((unfolded && !xpDependency) || optimization != null)
            {
                hostLang = "XQ";
                if (langVersion.Equals("2.0"))
                {
                    langVersion = "1.0";
                }
            }
            if (run)
            {

                Outcome outcome = null;
                string exp = null;
                try
                {
                    exp = xpc.Evaluate("if (test/@file) then unparsed-text(resolve-uri(test/@file, base-uri(.))) else string(test)", testCase).ToString();
                }
                catch (DynamicError err)
                {
                    Console.WriteLine("*** Failed to read query: " + err.Message);
                    outcome = new Outcome(err);
                }
               

                if (outcome == null)
                {
                    if (hostLang.Equals(("XP")))
                    {
                        XPathCompiler testXpc = env.xpathCompiler;
                        testXpc.XPathLanguageVersion = langVersion;
                        testXpc.DeclareNamespace("fn", JNamespaceConstant.FN);
                        testXpc.DeclareNamespace("xs", JNamespaceConstant.SCHEMA);
                        testXpc.DeclareNamespace("math", JNamespaceConstant.MATH);
                        testXpc.DeclareNamespace("map", JNamespaceConstant.MAP_FUNCTIONS);

                        try
                        {
                            XPathSelector selector = testXpc.Compile(exp).Load();
                            foreach (QName varName in env.params1.Keys)
                            {
                                selector.SetVariable(varName, env.params1[varName]);
                            }
                            if (env.contextNode != null)
                            {
                                selector.ContextItem = env.contextNode;
                            }
                            
                            selector.InputXmlResolver = new TestUriResolver(env);
                            
                            XdmValue result = selector.Evaluate();
                            outcome = new Outcome(result);
                        }
                        catch (DynamicError err)
                        {
                            Console.WriteLine(err.Message);
                            outcome = new Outcome(err);
                            
                        }
                        catch (StaticError err)
                        {
                            Console.WriteLine(err.Message);
                            outcome = new Outcome(err);

                        }
                        catch (Exception err)
                        {
                            Console.WriteLine("*** Failed to read query: " + err.Message);
                            outcome = new Outcome(new DynamicError("*** Failed to read query: " + err.Message));
                        }
                    }
                    else
                    {
                        XQueryCompiler testXqc = env.xqueryCompiler;
                        testXqc.XQueryLanguageVersion = langVersion;
                        testXqc.DeclareNamespace("fn", JNamespaceConstant.FN);
                        testXqc.DeclareNamespace("xs", JNamespaceConstant.SCHEMA);
                        testXqc.DeclareNamespace("math", JNamespaceConstant.MATH);
                        testXqc.DeclareNamespace("map", JNamespaceConstant.MAP_FUNCTIONS);
                        ErrorCollector errorCollector = new ErrorCollector();
                        //testXqc.setErrorListener(errorCollector);
                        string decVars = env.paramDecimalDeclarations.ToString();
                        if (decVars.Length != 0)
                        {
                            int x = (exp.IndexOf("(:%DECL%:)"));
                            if (x < 0)
                            {
                                exp = decVars + exp;
                            }
                            else
                            {
                                exp = exp.Substring(0, x) + decVars + exp.Substring(x + 13);
                            }
                        }
                        string vars = env.paramDeclarations.ToString();
                        if (vars.Length != 0)
                        {
                            int x = (exp.IndexOf("(:%VARDECL%:)"));
                            if (x < 0)
                            {
                                exp = vars + exp;
                            }
                            else
                            {
                                exp = exp.Substring(0, x) + vars + exp.Substring(x + 13);
                            }
                        }
                        ModuleResolver mr = new ModuleResolver(xpc);
                        mr.setTestCase(testCase);
                        testXqc.QueryResolver = (IQueryResolver)mr;

                        try
                        {
                            XQueryExecutable q = testXqc.Compile(exp);
                            if (optimization != null)
                            {
                             /*   XdmDestination expDest = new XdmDestination();
                                net.sf.saxon.Configuration config = driverProc.Implementation;
                                net.sf.saxon.trace.ExpressionPresenter presenter = new net.sf.saxon.trace.ExpressionPresenter(driverProc.Implementation, expDest.getReceiver(config));
                                //q.getUnderlyingCompiledQuery().explain(presenter);
                                presenter.close();
                                XdmNode explanation = expDest.XdmNode;
                                XdmItem optResult = xpc.EvaluateSingle(optimization.GetAttributeValue(new QName("assert")), explanation);
                                if ((bool)((XdmAtomicValue)optResult).Value)
                                {
                                    Console.WriteLine("Optimization result OK");
                                }
                                else
                                {
                                    Console.WriteLine("Failed optimization test");
                                    Serializer serializer = new Serializer();
                                    serializer.SetOutputWriter(Console.Error);
                                    driverProc.WriteXdmValue(explanation, serializer);
                                    WriteTestCaseElement(testCaseName, "fail", "Failed optimization assertions");
                                    failures++;
                                    return;
                                }*/

                            }
                            XQueryEvaluator selector = q.Load();
                            foreach (QName varName in env.params1.Keys)
                            {
                                selector.SetExternalVariable(varName, env.params1[varName]);
                            }
                            if (env.contextNode != null)
                            {
                                selector.ContextItem = env.contextNode;
                            }
                            selector.InputXmlResolver= new TestUriResolver(env);
                            XdmValue result = selector.Evaluate();
                            outcome = new Outcome(result);
                        }
                        catch (DynamicError err)
                        {
                            Console.WriteLine("TestSet" + testFuncSet);
                            Console.WriteLine(err.Message);
                            outcome = new Outcome(err);
                            outcome.setErrorsReported(errorCollector.getErrorCodes());
                        }
                        catch(StaticError err){
                            Console.WriteLine("TestSet" + testFuncSet);
                            Console.WriteLine(err.Message);
                            outcome = new Outcome(err);
                            outcome.setErrorsReported(errorCollector.getErrorCodes());
                        }
                        catch(Exception err){
                            Console.WriteLine("TestSet" + testFuncSet);
                            Console.WriteLine(err.Message);
                            outcome = new Outcome(new DynamicError(err.Message));
                            outcome.setErrorsReported(errorCollector.getErrorCodes());
                        }
                    }
                }
                XdmNode assertion;
                if (alternativeResult != null)
                {
                    assertion = (XdmNode)xpc.EvaluateSingle("*[1]", alternativeResult);
                }
                else
                {
                    assertion = (XdmNode)xpc.EvaluateSingle("result/*[1]", testCase);
                }
                if (assertion == null)
                {
                    Console.WriteLine("*** No assertions found for test case " + testCaseName);
                    WriteTestCaseElement(testCaseName, "fail", "No assertions in test case");
                    failures++;
                    return;
                }
                XPathCompiler assertXpc = env.processor.NewXPathCompiler();
                assertXpc.XPathLanguageVersion = "3.0";
                assertXpc.DeclareNamespace("fn", JNamespaceConstant.FN);
                assertXpc.DeclareNamespace("xs", JNamespaceConstant.SCHEMA);
                assertXpc.DeclareNamespace("math", JNamespaceConstant.MATH);
                assertXpc.DeclareNamespace("map", JNamespaceConstant.MAP_FUNCTIONS);
                assertXpc.DeclareVariable(new QName("result"));

                bool b = testAssertion(assertion, outcome, assertXpc, xpc, debug);
                if (b)
                {
                    Console.WriteLine("OK");
                    successes++;
                    feedback.Message("OK" + Environment.NewLine, false);
                    

                    WriteTestCaseElement(testCaseName, "full", null);


                }
                else
                {
                    

                    if (outcome.isException())
                    {
                        XdmItem expectedError = xpc.EvaluateSingle("result//error/@code", testCase);

                        if (expectedError == null)
                        {
                            //                        if (debug) {
                            //                            outcome.getException().printStackTrace(System.out);
                            //                        }
                            if (outcome.getException() is StaticError)
                            {
                                WriteTestCaseElement(testCaseName, "fail", "Expected success, got " + ((StaticError)outcome.getException()).ErrorCode);
                                feedback.Message("*** fail, result " + ((StaticError)outcome.getException()).ErrorCode.LocalName +
                                        " Expected success." + Environment.NewLine, false);
                            }
                            else
                            {
                                WriteTestCaseElement(testCaseName, "fail", "Expected success, got " + ((DynamicError)outcome.getException()).ErrorCode);
                                feedback.Message("*** fail, result " + ((DynamicError)outcome.getException()).ErrorCode.LocalName +
                                        " Expected success." + Environment.NewLine, false);
                            }
                            failures++;
                        }
                        else
                        {
                            if (outcome.getException() is StaticError)
                            {
                                WriteTestCaseElement(testCaseName, "different-error", "Expected error:" + expectedError.ToString() /*.GetstringValue()*/ + ", got " + ((StaticError)outcome.getException()).ErrorCode.ToString());
                                feedback.Message("*** fail, result " + ((StaticError)outcome.getException()).ErrorCode.LocalName +
                                        " Expected error:" + expectedError.ToString() + Environment.NewLine, false);
                            }
                            else
                            {
                                WriteTestCaseElement(testCaseName, "different-error", "Expected error:" + expectedError.ToString() /*.GetstringValue()*/ + ", got " + ((DynamicError)outcome.getException()).ErrorCode.ToString());
                                feedback.Message("*** fail, result " + ((DynamicError)outcome.getException()).ErrorCode.LocalName +
                                        " Expected error:" + expectedError.ToString() + Environment.NewLine, false);
                            }
                            wrongErrorResults++;
                        }

                    }
                    else
                    {
                        try
                        {
                            WriteTestCaseElement(testCaseName, "fail", "Wrong results, got " + truncate(outcome.serialize(assertXpc.Processor)));
                        }catch (Exception) {
                            WriteTestCaseElement(testCaseName, "fail", "Wrong results, got ");
                        }
                        failures++;
                        if (debug)
                        {
                            try
                            {
                                feedback.Message("Result:" + Environment.NewLine, false);
                               // driverProc.WriteXdmValue(outcome.getResult(), driverSerializer);
                                feedback.Message("=======" + Environment.NewLine, false);
                            }
                            catch (Exception)
                            {
                            }
                            feedback.Message(outcome.getResult() + Environment.NewLine, false);
                        }
                        else
                        {
                            feedback.Message("*** fail (use -debug to show actual result)" + Environment.NewLine, false);
                        }
                    }
                    
                }
                feedback.Feedback(successes, failures, 25693);
            }
        }

        private string truncate(string in1)
        {
            if (in1.Length > 80)
            {
                return in1.Substring(0, 80) + "...";
            }
            else
            {
                return in1;
            }
        }

        private bool testAssertion(XdmNode assertion, Outcome outcome, XPathCompiler assertXpc, XPathCompiler catalogXpc, bool debug)
        {
            try
            {
                string tag = assertion.NodeName.LocalName;
                bool result = testAssertion2(assertion, outcome, assertXpc, catalogXpc, debug);
                if (debug && !("all-of".Equals(tag)) && !("any-of".Equals(tag)))
                {
                    feedback.Message("Assertion " + tag + " (" + assertion.StringValue + ") " + (result ? " succeeded" : " failed"), false);
                    if (tag.Equals("error"))
                    {
                        Console.WriteLine("Expected exception " + assertion.GetAttributeValue(new QName("code")) +
                                ", got " + (outcome.isException() ? ((DynamicError)outcome.getException()).ErrorCode.ToString() : "success"));
                    }
                }
                return result;
            }
            catch (Exception e)
            {
                //e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
                return false;
            }
        }

        private bool testAssertion2(XdmNode assertion, Outcome outcome, XPathCompiler assertXpc, XPathCompiler catalogXpc, bool debug)
        {
            string tag = assertion.NodeName.LocalName;

            if (tag.Equals("assert-eq"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XPathSelector s = assertXpc.Compile("$result eq " + assertion.StringValue).Load();
                    s.SetVariable(new QName("result"), outcome.getResult());
                    XdmAtomicValue item = (XdmAtomicValue)s.EvaluateSingle();
                    if (s == null)
                    {
                        return false;
                    }
                    return (bool)item.Value;
                }
            }
            if (tag.Equals("assert-deep-eq"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XPathSelector s = assertXpc.Compile("deep-equal($result , (" + assertion.StringValue + "))").Load();
                    s.SetVariable(new QName("result"), outcome.getResult());
                    return (bool)((XdmAtomicValue)s.Evaluate()).Value;
                }
            }
            else if (tag.Equals("assert-permutation"))
            {
                // TODO: extend this to handle nodes (if required)
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    try
                    {
                        int expectedItems = 0;
                        Hashtable expected = new Hashtable();
                        XPathSelector s = assertXpc.Compile("(" + assertion.StringValue + ")").Load();
                        s.SetVariable(new QName("result"), outcome.getResult()); // not used, but we declared it
                        net.sf.saxon.lib.StringCollator collator = net.sf.saxon.expr.sort.CodepointCollator.getInstance();
                        net.sf.saxon.expr.XPathContext context = new net.sf.saxon.expr.XPathContextMajor(net.sf.saxon.value.StringValue.EMPTY_STRING, assertXpc.Processor.Implementation);
                    /*    foreach (XdmItem item in s) {
                            expectedItems++;
                            XdmValue value = (XdmValue) item;
                            Object comparable = value.isNaN() ?
                                    AtomicSortComparer.COLLATION_KEY_NaN :
                                    value.getXPathComparable(false, collator, context);
                            expected.add(comparable);
                        } */
                        int actualItems = 0;
                        /*foreach (XdmItem item in outcome.getResult()) {
                            actualItems++;
                            AtomicValue value = (AtomicValue) item.getUnderlyingValue();
                            Object comparable = value.isNaN() ?
                                    AtomicSortComparer.COLLATION_KEY_NaN :
                                    value.getXPathComparable(false, collator, context);
                            if (!expected.Contains(comparable)) {
                                return false;
                            }
                        }*/
                        return actualItems == expectedItems;
                    }
                    catch (DynamicError e)
                    {
                        return false;
                    }
                }
            }
            else if (tag.Equals("assert-serialization"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    string normalizeAtt = assertion.GetAttributeValue(new QName("normalize-space"));
                    bool normalize = normalizeAtt != null && ("true".Equals(normalizeAtt.Trim()) || "1".Equals(normalizeAtt.Trim()));
                    string ignoreAtt = assertion.GetAttributeValue(new QName("ignore-prefixes"));
                    bool ignorePrefixes = ignoreAtt != null && ("true".Equals(ignoreAtt.Trim()) || "1".Equals(ignoreAtt.Trim()));
                    catalogXpc.BaseUri = "";
                    string comparand = catalogXpc.Evaluate("if (@file) then unparsed-text(resolve-uri(@file, base-uri(.))) else string(.)", assertion).ToString();
                    if (normalize)
                    {
                        comparand = net.sf.saxon.value.Whitespace.collapseWhitespace(comparand).ToString();
                    }
                    StringWriter tw = new StringWriter();
                    
                    Serializer serializer = new Serializer();
                    serializer.SetOutputWriter(tw);
                    serializer.SetOutputProperty(Serializer.METHOD, "xml");
                    serializer.SetOutputProperty(Serializer.INDENT, "no");
                    serializer.SetOutputProperty(Serializer.OMIT_XML_DECLARATION, "yes");
                    assertXpc.Processor.WriteXdmValue(outcome.getResult(), serializer);
                    if (comparand.Equals(tw.ToString())) {
                        return true;
                    }
                    DocumentBuilder builder = assertXpc.Processor.NewDocumentBuilder();
                    StringReader reader = new StringReader("<z>" + comparand + "</z>");
                    builder.BaseUri = assertion.BaseUri;
                    XdmNode expected = builder.Build(reader);
                    
                    int flag = 0;

                    flag |= net.sf.saxon.functions.DeepEqual.INCLUDE_COMMENTS;
                    flag |= net.sf.saxon.functions.DeepEqual.INCLUDE_PROCESSING_INSTRUCTIONS;
                    if (!ignorePrefixes)
                    {
                        flag |= net.sf.saxon.functions.DeepEqual.INCLUDE_NAMESPACES;
                        flag |= net.sf.saxon.functions.DeepEqual.INCLUDE_PREFIXES;
                    }
                    flag |= net.sf.saxon.functions.DeepEqual.COMPARE_STRING_VALUES;
                    flag |= net.sf.saxon.functions.DeepEqual.WARNING_IF_FALSE;
                    try
                    {
                       net.sf.saxon.om.SequenceIterator iter0;
                       XdmValue v = outcome.getResult();
                       if (v.Count == 1 && v is XdmNode && ((XdmNode)v).NodeKind == XmlNodeType.Document)
                         {
                             iter0 = ((XdmNode)v).Implementation.iterateAxis(net.sf.saxon.om.Axis.CHILD);
                         } else {
                             iter0 = net.sf.saxon.value.Value.asIterator(outcome.getResult().Unwrap());
                         }
                         net.sf.saxon.om.SequenceIterator iter1 = (expected.Implementation.iterateAxis(net.sf.saxon.om.Axis.CHILD).next()).iterateAxis(net.sf.saxon.om.Axis.CHILD);
                         return net.sf.saxon.functions.DeepEqual.deepEquals(
                                 iter0, iter1,
                                 new net.sf.saxon.expr.sort.GenericAtomicComparer(net.sf.saxon.expr.sort.CodepointCollator.getInstance(), null),
                                 assertXpc.Processor.Implementation, flag);
                    }
                    catch (DynamicError e)
                    {
                        // e.printStackTrace();
                        return false;
                    }
                }
            }
            else if (tag.Equals("assert-serialization-error"))
            {
                  if (outcome.isException()) {
                      return false;
                  } else {
                      string expectedError = assertion.GetAttributeValue(new QName("code"));
                      StringWriter sw = new StringWriter();
                      Serializer serializer = new Serializer();
                      serializer.SetOutputWriter(sw);
                      serializer.SetOutputProperty(Serializer.METHOD, "xml");
                      serializer.SetOutputProperty(Serializer.INDENT, "no");
                      serializer.SetOutputProperty(Serializer.OMIT_XML_DECLARATION, "yes");
                      try {
                          assertXpc.Processor.WriteXdmValue(outcome.getResult(), serializer);
                          return false;
                      } catch (DynamicError err) {
                          bool b = expectedError.Equals(err.ErrorCode.LocalName);
                          if (!b)
                          {
                            feedback.Message("Expected " + expectedError + ", got " + err.ErrorCode.LocalName, false);
                          }
                          return true;
                      }
                  }
            }
            else if (tag.Equals("assert-empty"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XdmValue result = outcome.getResult();
                    return result.Count == 0;
                }
            }
            else if (tag.Equals("assert-count"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XdmValue result = outcome.getResult();
                    return result.Count == int.Parse(assertion.StringValue);
                }
            }
            else if (tag.Equals("assert"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XPathSelector s = assertXpc.Compile(assertion.StringValue).Load();
                    s.SetVariable(new QName("result"), outcome.getResult());
                    return (bool)((XdmAtomicValue)s.EvaluateSingle()).Value;
                }
            }
            else if (tag.Equals("assert-string-value"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XdmValue resultValue = outcome.getResult();
                    string resultstring;
                    string assertionstring = assertion.StringValue;
                    if (resultValue is XdmNode)
                    {
                        resultstring = ((XdmNode)resultValue).StringValue;
                    }else if(resultValue is XdmAtomicValue){
                        resultstring = ((XdmAtomicValue)resultValue).ToString();
                    }
                    else
                    {
                        bool first = true;
                        StringBuilder fsb = new StringBuilder(256);
                        foreach (XdmItem item in resultValue)
                        {
                            if (first)
                            {
                                first = false;
                            }
                            else
                            {
                                fsb.Append(' ');
                            }
                            fsb.Append(item.Unwrap().getStringValue());
                        }
                        resultstring = fsb.ToString();
                    }
                    string normalizeAtt = assertion.GetAttributeValue(new QName("normalize-space"));
                    if (normalizeAtt != null && (normalizeAtt.Trim().Equals("true") || normalizeAtt.Trim().Equals("1")))
                    {
                        assertionstring = net.sf.saxon.value.Whitespace.collapseWhitespace(assertionstring).ToString();
                        resultstring = net.sf.saxon.value.Whitespace.collapseWhitespace(resultstring).ToString();
                    }
                    if (resultstring.Equals(assertionstring))
                    {
                        return true;
                    }
                    else
                    {
                        if (debug)
                        {
                            if (resultstring.Length != assertionstring.Length)
                            {
                                Console.WriteLine("Result length " + resultstring.Length + "; expected length " + assertionstring.Length);
                            }
                            int len = Math.Min(resultstring.Length, assertionstring.Length);
                            for (int i = 0; i < len; i++)
                            {
                                if (resultstring[i] != assertionstring[i])
                                {
                                    feedback.Message("Results differ at index " + i +
                                            "(\"" + resultstring.Substring(i, (i + 10 > len ? len : i + 10)) + "\") vs (\"" +
                                            assertionstring.Substring(i, (i + 10 > len ? len : i + 10)) + "\")", false);
                                    break;
                                }
                            }
                        }
                        return false;
                    }
                }
            }
            else if (tag.Equals("assert-type"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XPathSelector s = assertXpc.Compile("$result instance of " + assertion.StringValue).Load();
                    s.SetVariable(new QName("result"), outcome.getResult());
                    return (bool)((XdmAtomicValue)s.EvaluateSingle()).Value;
                }
            }
            else if (tag.Equals("assert-true"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XdmValue result = outcome.getResult();
                    return result.Count == 1  && ((XdmItem)result).IsAtomic() &&
                        ((XdmAtomicValue)result).GetPrimitiveTypeName().Equals(QName.XS_BOOLEAN) &&
                        (((XdmAtomicValue)result).GetBooleanValue());
                }
            }
            else if (tag.Equals("assert-false"))
            {
                if (outcome.isException())
                {
                    return false;
                }
                else
                {
                    XdmValue result = outcome.getResult();
                    return result.Count == 1 &&
                           ((XdmItem)result.Simplify).IsAtomic() &&
                            ((XdmAtomicValue)result.Simplify).GetPrimitiveTypeName().Equals(QName.XS_BOOLEAN) &&
                            !(bool)((XdmAtomicValue)result.Simplify).Value;
                }
            }
            else if (tag.Equals("error"))
            {
                string expectedError = assertion.GetAttributeValue(new QName("code"));
                //noinspection ThrowableResultOfMethodCallIgnored
                Exception err = outcome.getException();
                QName errorCode = null;
                if (err is DynamicError)
                {
                    errorCode = ((DynamicError)outcome.getException()).ErrorCode;
                }
                else {
                    errorCode = ((StaticError)outcome.getException()).ErrorCode;
                }
                 return outcome.isException() &&
                            (expectedError.Equals("*") ||
                                    (errorCode != null &&
                                            errorCode.LocalName.Equals(expectedError)) ||
                                    (outcome.hasReportedError(expectedError)));
                
            }
            else if (tag.Equals("all-of"))
            {
                XdmValue children = catalogXpc.Evaluate("*", assertion);
                foreach (XdmItem child in children)
                {
                    if (!testAssertion((XdmNode)child, outcome, assertXpc, catalogXpc, debug))
                    {
                        return false;
                    }
                }
                return true;
            }
            else if (tag.Equals("any-of"))
            {
                XdmValue children = catalogXpc.Evaluate("*", assertion);
                foreach (XdmItem child in children)
                {
                    if (testAssertion((XdmNode)child, outcome, assertXpc, catalogXpc, debug))
                    {
                        return true;
                    }
                }
                return false;
            }
            throw new Exception("Unknown assertion element " + tag);
        }


        public void WriteResultFilePreamble(Processor processor, XdmNode catalog, string date)/* throws IOException, SaxonApiException, XMLStreamException*/ {

            ///   results = new StreamWriter(/*TODO saxonResultsDir + */"/results"
            //            + processor.ProductVersion + "n.xml");

            /*Writer resultWriter = new BufferedWriter(new FileWriter(new File(resultsDir + "/results"
                    + Version.getProductVersion() + ".xml")));
            Serializer serializer = processor.NewSerializer(resultWriter);
            serializer.setOutputProperty(Serializer.Property.METHOD, "xml");
            serializer.setOutputProperty(Serializer.Property.INDENT, "yes");
            serializer.setOutputProperty(Serializer.Property.SAXON_LINE_LENGTH, "120");*/
            //results = serializer.GetResult();// .getXMLStreamWriter();
            
            results = new StreamWriter(resultsDir + "/results"
                        + processor.ProductVersion + "n.xml");

            
            results.WriteLine("<FOTS-test-suite-result>");
            // results.writeDefaultNamespace(RNS);
            results.WriteLine("<implementation name='Saxon-EE' version='" + processor.ProductVersion + "' anonymous-result-column='false'    >");
            //  results.writeAttribute("version", Version.getProductVersion());
            results.WriteLine("<organization name='http://www.saxonica.com/' anonymous='false' />");
            results.WriteLine("<submitter name='ONeil Delpratt' email='oneil@saxonica.com' />");
            results.WriteLine("</implementation>"); //implementation
            results.WriteLine("<test-run date='" + date + "' testSuiteVersion='" + catalog.GetAttributeValue(new QName("test-suite")) + " " + catalog.GetAttributeValue(new QName("version")) + "'/>");

        }

        private void writeResultFilePostamble()
        {
            results.WriteLine("</FOTS-test-suite-result>"); //test-suite-result
            results.Close();
        }

        private void WriteTestCaseElement(string name, string result, string comment)
        {
            try
            {
                results.WriteLine("<testcase name='" + name + "' result='" + result + "' " + (comment != null ? "comment='" + comment + "'" : "") + " />");
                /*if (comment != null) {
                    results.writeAttribute("comment", comment);
                }*/
            }
            catch (DynamicError ex)
            {
            }
        }

        /**
         * Implement extension function fots:copy() which copies an existing node to create
         * a new parentless node. Needed because XPath cannot create parentless nodes directly
         */

        private class FotsCopyFunction /*: ExtensionFunctionDefinition*/
        {

            public QName GetFunctionQName()
            {
                return new QName("", "http://www.w3.org/2010/09/qt-fots-catalog", "copy");
            }


            public int GetMinimumNumberOfArguments()
            {
                return 1;
            }


            public int GetMaximumNumberOfArguments()
            {
                return 1;
            }


            /*public SequenceType[] getArgumentTypes() {
                return new SequenceType[]{SequenceType.SINGLE_NODE};
            }*/


            /*public SequenceType getResultType(SequenceType[] suppliedArgumentTypes) {
                return SequenceType.SINGLE_NODE;
            }*/


            public bool hasSideEffects()
            {
                return true;
            }


            public ExtensionFunctionCall makeCallExpression()
            {
                return null;
                /*TODO new ExtensionFunctionCall() {
                    public SequenceIterator call(SequenceIterator[] arguments, XPathContext context) throws XPathException {
                        NodeInfo node = (NodeInfo) arguments[0].next();
                        if (node == null) {
                            return EmptyIterator.getInstance();
                        } else {
                            switch (node.getNodeKind()) {
                                case Type.ELEMENT:
                                case Type.DOCUMENT: {
                                    Builder builder = context.getController().makeBuilder();
                                    builder.open();
                                    node.copy(builder, NodeInfo.ALL_NAMESPACES, 0);
                                    builder.close();
                                    return SingleNodeIterator.makeIterator(builder.getCurrentRoot());
                                }
                                case Type.ATTRIBUTE:
                                case Type.TEXT:
                                case Type.PROCESSING_INSTRUCTION:
                                case Type.COMMENT:
                                case Type.NAMESPACE:
                                    Orphan orphan = new Orphan(context.getConfiguration());
                                    orphan.setNodeKind((short) node.getNodeKind());
                                    orphan.setNodeName(new NameOfNode(node));
                                    orphan.setstringValue(node.getstringValue());
                                    return SingleNodeIterator.makeIterator(orphan);
                                default:
                                    throw new IllegalArgumentException("Unknown node kind " + node.getNodeKind());
                            }
                        }
                    }
                };*/
            }

        }


            public class ModuleResolver : IQueryResolver
            {

                XPathCompiler catXPC;
                XdmNode testCase;
                XmlUrlResolver resolver;

                public ModuleResolver(XPathCompiler xpc)
                {
                    this.catXPC = xpc;
                    resolver = new XmlUrlResolver();
                   
                }

                public void setTestCase(XdmNode testCase)
                {
                    this.testCase = testCase;
                }

                public Object GetEntity(Uri absoluteUri)
                {
                    String u = absoluteUri.ToString();
                    if (u.StartsWith("file:///"))
                    {
                        u = u.Substring(8);
                    }
                    else if (u.StartsWith("file:/"))
                    {
                        u = u.Substring(6);
                    }
                    return new FileStream(u, FileMode.Open, FileAccess.Read, FileShare.Read);
                }

                public Uri[] GetModules(string moduleUri, Uri baseUri, string[] locations)
                {
                       try {
                           XdmValue files = catXPC.Evaluate("./module[@uri='" + moduleUri + "']/@file/string()", testCase);
                           if (files.Count == 0) {
                               throw new DynamicError("Failed to find module entry for " + moduleUri);
                           }

                           Uri[] ss = new Uri[files.Count];
                           int i = 0;
                           foreach(XdmItem nodei in files){
                               ss[i] = resolver.ResolveUri(testCase.BaseUri, nodei.ToString());
                               i++;
                           }
                          
                           return ss;
                       } catch (Exception e) {
                           throw new DynamicError(e.Message);
                       }
                   } 
            }

            public class TestUriResolver : XmlUrlResolver
            {
                TestEnvironment env1;

                public TestUriResolver(TestEnvironment env)
                {
                    this.env1 = env;
                }

                public override Uri ResolveUri(Uri base1, string href)
                {
                    XdmNode node = null;
                    try
                    {
                        node = env1.sourceDocs[href];
                    } catch(Exception) {
                        return (new XmlUrlResolver()).ResolveUri(base1, href);
                    
                    }
                    if (node == null)
                    {
                        return null;
                    }
                    else
                    {
                        return node.DocumentUri;
                    }
                }
            }

            private class LazyLiteralInjector /*: net.sf.saxon.expr.parser.CodeInjector*/
            {
                /*  public Expression inject(Expression exp, StaticContext env, int construct, StructuredQName qName) {
                      if (exp is Literal) {
                          StructuredQName name = new StructuredQName("saxon", JNamespaceConstant.SAXON, "lazy-literal");
                          JavaExtensionFunctionCall wrapper = new JavaExtensionFunctionCall();
                          try {
                              wrapper.init(name, FOTestSuiteDriver.class,
                                      FOTestSuiteDriver.class.getMethod("lazyLiteral", ValueRepresentation.class),
                                      env.getConfiguration());
                              wrapper.setArguments(new Expression[]{exp});
                          } catch (NoSuchMethodException e) {
                              throw new IllegalStateException(e);
                          }
                          return wrapper;
                      } else {
                          return exp;
                      }
                  }*/
            }

            /**
             * Static method called as an external function call to evaluate a literal when running in "unfolded" mode.
             * The function simply returns the value of its argument - but the optimizer doesn't know that, so it
             * can't pre-evaluate the call at compile time.
             *
             * @param value the value to be returned
             * @return the supplied value, unchanged
             */

            /*public static ValueRepresentation lazyLiteral(ValueRepresentation value) {
                return value;
            }*/

            public class ErrorCollector /*: net.sf.saxon.lib.StandardErrorListener*/
            {

                private Hashtable errorCodes = new Hashtable();


                public void error(DynamicError exception)
                {
                    addErrorCode(exception);
                   // base.error;

                }


                public void fatalError(DynamicError exception)
                {
                    addErrorCode(exception);
                    //super.fatalError(exception);
                }

                /**
                 * Make a clean copy of this ErrorListener. This is necessary because the
                 * standard error listener is stateful (it remembers how many errors there have been)
                 *
                 * @param hostLanguage the host language (not used by this implementation)
                 * @return a copy of this error listener
                 */

                /*public DynamicError StandardErrorListener makeAnother(int hostLanguage)
                {
                    return DynamicError();
                }*/

                private void addErrorCode(DynamicError exception)
                {
                    //if (exception is XPathException) {
                    string errorCode = exception.ErrorCode.ToString();
                    if (errorCode != null)
                    {
                        errorCodes.Add(errorCode, true);
                    }
                    //}
                }

                public Hashtable getErrorCodes()
                {
                    return errorCodes;
                }
            }

    }