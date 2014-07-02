using System;
using System.IO;
using System.Collections;
using System.Xml;
using System.Text;
using Saxon.Api;
using TestRunner;

/// <summary>
/// Test suite driver for running the XQTS test suite against Saxon on .NET.
/// </summary>
/// <remarks>
/// <paraThe test suite directory must contain a subdirectory named SaxonDriver.
/// In this subdirectory there must be a document named exceptions.xml, containing</para>
/// <example><![CDATA[
/// <exceptions>
///   <exception>
///     <tests>trivial-1 trivial-2 trivial-3 trivial-4</tests>
///     <description>No support in Saxon for trivial embedding feature</description>
///   </exception>
/// </exceptions>
/// ]]></example>
/// <para>The SaxonDriver directory should also have a subdirectory named <c>results</c>,
/// with the same structure as the supplied <c>expectedResults</c> directory.</para>
/// <para>Note that the submitted results for Saxon were obtained with the Java product;
/// this driver will produce different results. <b>At present this test driver is
/// reporting many spurious test failures where the results are in fact correct.</b></para>
/// </remarks>


public class XQueryTestSuiteDriver
{
    static void MainXXX(string[] args)
    {
        if (args.Length == 0 || args[0].Equals("-?"))
        {
            Console.WriteLine("XQueryTestSuiteDriver testsuiteDir resultsDir testName?");
        }
        try
        {
            new XQueryTestSuiteDriver().go(args);
        }
        catch (Exception e)
        {
            Console.WriteLine(e.Message);
            Console.WriteLine(e.StackTrace);
        }
    }

    String testURI = "http://www.w3.org/2005/02/query-test-XQTSCatalog";
    String testSuiteDir;
    String saxonResultsDir;
    Processor processor = new Processor(true, true);  // processor is schema-aware
    
    // TODO: change to (true, false) when not debugging

    FileComparer fileComparer;
    IFeedbackListener feedback;
    int passed = 0;
    int failed = 0;
    int total = 0;

    XPathExecutable findSourcePath;
    XPathExecutable findCollection;
    XPathExecutable findModule;


    string testPattern = null;
    
    StreamWriter results;
    StreamWriter log;


    private XdmNode getChildElement(XdmNode parent, QName child)
    {
        IEnumerator e = parent.EnumerateAxis(XdmAxis.Child, child);
        return e.MoveNext() ? (XdmNode)e.Current : null;
    }

    public void setFeedbackListener(IFeedbackListener f)
    {
        feedback = f;
    }


    public void go(String[] args)
    {

        
        processor.SetProperty("http://saxon.sf.net/feature/trace-external-functions", "true");
        testSuiteDir = args[0];
        if (testSuiteDir.EndsWith("/"))
        {
            testSuiteDir = testSuiteDir.Substring(0, testSuiteDir.Length - 1);
        }
        saxonResultsDir = args[1];
        if (saxonResultsDir.EndsWith("/"))
        {
            saxonResultsDir = saxonResultsDir.Substring(0, testSuiteDir.Length - 1);
        }
        Hashtable exceptions = new Hashtable();

        if (args.Length > 1)
        {
            testPattern = (args[2]); // TODO: allow a regex
        }

        for (int i = 0; i < args.Length; i++)
        {
            if (args[i].Equals("-w"))
            {
                //showWarnings = true;
            }
            
        }

        fileComparer = new FileComparer(processor, testSuiteDir);

        XPathCompiler xpc = processor.NewXPathCompiler();
        xpc.DeclareNamespace("t", testURI);
        xpc.DeclareVariable(new QName("", "param"));
        findSourcePath = xpc.Compile("//t:test-suite/t:sources/t:source[@ID=$param]");

        findCollection = xpc.Compile("//t:test-suite/t:sources/t:collection[@ID=$param]");

        xpc = processor.NewXPathCompiler();
        xpc.DeclareNamespace("t", testURI);
        xpc.DeclareVariable(new QName("", "testcase"));
        xpc.DeclareVariable(new QName("", "moduleuri"));
        findModule = xpc.Compile("for $m in $testcase/t:module[@namespace=$moduleuri] " +
            "return concat('file:///" + testSuiteDir +
            "/', root($testcase)/t:test-suite/t:sources/t:module[@ID=string($m)]/@FileName, '.xq')");

        //xpc = processor.NewXPathCompiler();
        //xpc.DeclareNamespace("saxon", "http://saxon.sf.net/");
        //xpc.DeclareVariable(new QName("", "actual"));
        //xpc.DeclareVariable(new QName("", "gold"));
        //xpc.DeclareVariable(new QName("", "debug"));
        //compareDocuments = xpc.Compile("saxon:deep-equal($actual, $gold, (), if ($debug) then 'JNCPS?!' else 'JNCPS')");

        QName testCaseNT = new QName(testURI, "test-case");
        QName nameNT = new QName(testURI, "name");
        QName queryNT = new QName(testURI, "query");
        QName inputNT = new QName(testURI, "input");
        QName inputFileNT = new QName(testURI, "input-file");
        QName inputUriNT = new QName(testURI, "input-URI");
        QName defaultCollectionNT = new QName(testURI, "defaultCollection");
        QName outputFileNT = new QName(testURI, "output-file");
        QName expectedErrorNT = new QName(testURI, "expected-error");
        QName schemaNT = new QName(testURI, "schema");
        QName contextItemNT = new QName(testURI, "contextItem");
        QName inputQueryNT = new QName(testURI, "input-query");
        QName sourceDocumentNT = new QName(testURI, "source-document");
        QName errorNT = new QName(testURI, "error");
        QName validationNT = new QName(testURI, "validation");
        QName discretionaryItemsNT = new QName(testURI, "discretionary-items");
        QName discretionaryFeatureNT = new QName(testURI, "discretionary-feature");
        QName discretionaryChoiceNT = new QName(testURI, "discretionary-choice");
        QName initialContextNodeNT = new QName(testURI, "initial-context-node");


        QName fileAtt = new QName("", "file");
        QName filePathAtt = new QName("", "FilePath");
        QName fileNameAtt = new QName("", "FileName");
        QName errorIdAtt = new QName("", "error-id");
        QName compareAtt = new QName("", "compare");
        QName nameAtt = new QName("", "name");
        QName behaviorAtt = new QName("", "behavior");
        QName qnameAtt = new QName("", "qname");
        QName modeAtt = new QName("", "mode");
        QName validatesAtt = new QName("", "validates");
        QName variableAtt = new QName("", "variable");
        QName roleAtt = new QName("", "role");

        DocumentBuilder builder = processor.NewDocumentBuilder();
        XdmNode exceptionsDoc = builder.Build(new Uri(saxonResultsDir + "/exceptions-n.xml"));

        // The exceptions.xml file contains details of tests that aren't to be run, for example
        // because they have known bugs or require special configuration

        IEnumerator exceptionTestCases = exceptionsDoc.EnumerateAxis(XdmAxis.Descendant, new QName("", "exception"));
        while (exceptionTestCases.MoveNext())
        {
            XdmNode n = (XdmNode)exceptionTestCases.Current;
            String nameAttVal = n.StringValue;
            char[] seps = { ' ', '\n', '\t' };
            String[] parts = nameAttVal.Split(seps);
            foreach (string p in parts)
            {
                if (!exceptions.ContainsKey(p))
                {
                    exceptions.Add(p, "Exception");
                }
            }
        }

        // Hash table containing all source documents. The key is the document name in the
        // catalog, the value is the corresponding document node

        Hashtable sourceDocs = new Hashtable(50);

        // Load the catalog

        XdmNode catalog = builder.Build(new Uri(testSuiteDir + "/XQTScatalog.xml"));

        // Add all Static Typing test cases to the exceptions list

        xpc = processor.NewXPathCompiler();
        xpc.DeclareNamespace("t", testURI);
        XPathSelector st = xpc.Compile("//t:test-group[@name='StaticTyping']//t:test-case").Load();
        st.ContextItem = catalog;
        IEnumerator ste = st.GetEnumerator();
        while (ste.MoveNext())
        {
            XdmNode testCase = (XdmNode)ste.Current;
            exceptions.Add(testCase.GetAttributeValue(nameAtt), "StaticTypingException");
        }

        // Create the results file and log file

        results = new StreamWriter(saxonResultsDir + "/results"
                    + processor.ProductVersion + "n.xml");
        log = new StreamWriter(saxonResultsDir + "/log"
                    + processor.ProductVersion + "n.xml");
        
        log.WriteLine("Testing Saxon " + processor.ProductVersion);
        results.WriteLine("<test-suite-result xmlns='http://www.w3.org/2005/02/query-test-XQTSResult'>");

        // Pre-load all the schemas

        SchemaManager mgr = processor.SchemaManager;
        IEnumerator se = catalog.EnumerateAxis(XdmAxis.Descendant, schemaNT);
        while (se.MoveNext())
        {
            XdmNode schemaNode = (XdmNode)se.Current;
            log.WriteLine("Loading schema " + schemaNode.GetAttributeValue(fileNameAtt));
            Uri location = new Uri(testSuiteDir + "/" + schemaNode.GetAttributeValue(fileNameAtt));
            mgr.Compile(location);
        }

        total = 0;
        IEnumerator testCases = catalog.EnumerateAxis(XdmAxis.Descendant, testCaseNT);
        while (testCases.MoveNext()) {
            total++;
        }

        // Process the test cases in turn

        testCases = catalog.EnumerateAxis(XdmAxis.Descendant, testCaseNT);
        while (testCases.MoveNext())
        {
            XdmNode testCase = (XdmNode)testCases.Current;

            String testName = testCase.GetAttributeValue(nameAtt);
            if (testPattern != null && !testName.StartsWith(testPattern))
            {
                continue;
            }
            if (exceptions.ContainsKey(testName))
            {
                continue;
            }

            log.WriteLine("Test " + testName);


            // Compile the query

            String errorCode = null;

            String filePath = testCase.GetAttributeValue(filePathAtt);
            XdmNode query = getChildElement(testCase, queryNT);
            String queryName = query.GetAttributeValue(nameAtt);
            String queryPath = testSuiteDir + "/Queries/XQuery/" + filePath + queryName + ".xq";

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.BaseUri = new Uri(queryPath).ToString();
            compiler.QueryResolver = new XqtsModuleResolver(testCase, findModule);
            compiler.SchemaAware = true;
                // Set all queries to schema-aware, because we don't really know whether they will have to handle typed input or not.

            ArrayList errors = new ArrayList();
            compiler.ErrorList = errors;
            XQueryEvaluator xqe = null;
            FileStream stream = null;
            try
            {
                stream = new FileStream(queryPath, FileMode.Open, FileAccess.Read, FileShare.Read);
                xqe = compiler.Compile(stream).Load();
            }
            catch (Exception e)
            {
                if (errors.Count > 0 && ((StaticError)errors[0]).ErrorCode != null)
                {
                    errorCode = ((StaticError)errors[0]).ErrorCode.LocalName;
                }
                else if (e is StaticError && ((StaticError)e).ErrorCode != null)
                {
                    log.WriteLine(e.Message);
                    errorCode = ((StaticError)e).ErrorCode.LocalName;
                }
                else
                {
                    log.WriteLine(e.Message);
                    errorCode = "ErrorXXX";
                }
            }
            finally
            {
                if (stream != null)
                {
                    stream.Close();
                }
            }

            // if the query compiled successfully, try to run it

            String outputPath = null;
            if (errorCode == null && xqe != null)
            {

                // Supply any input documents

                IEnumerator en = testCase.EnumerateAxis(XdmAxis.Child, inputFileNT);
                while (en.MoveNext())
                {
                    XdmNode file = (XdmNode)en.Current;
                    String var = file.GetAttributeValue(variableAtt);
                    if (var != null)
                    {
                        String sourceName = file.StringValue;
                        XdmNode sourceDoc;
                        if (sourceDocs.ContainsKey(sourceName))
                        {
                            sourceDoc = (XdmNode)sourceDocs[sourceName];
                        }
                        else
                        {
                            sourceDoc = buildSource(catalog, builder, sourceName);
                            sourceDocs.Add(sourceName, sourceDoc);
                        }
                        xqe.SetExternalVariable(new QName("", var), sourceDoc);
                    }
                }

                // Supply any input URIs

                IEnumerator eu = testCase.EnumerateAxis(XdmAxis.Child, inputUriNT);
                while (eu.MoveNext())
                {
                    XdmNode file = (XdmNode)eu.Current;
                    String var = file.GetAttributeValue(variableAtt);
                    if (var != null)
                    {
                        String sourceName = file.StringValue;
                        if (sourceName.StartsWith("collection"))
                        {
                            // Supply a collection URI. 
                            // This seems to be the only way to distinguish a document URI 
                            // from a collection URI.
                            String uri = "collection:" + sourceName;
                            XPathSelector xpe = findCollection.Load();
                            xpe.SetVariable(new QName("", "param"), new XdmAtomicValue(sourceName));
                            xpe.ContextItem = catalog;
                            XdmNode collectionNode = (XdmNode)xpe.EvaluateSingle();
                            if (collectionNode == null)
                            {
                                log.WriteLine("*** Collection " + sourceName + " not found");
                            }
                            processor.RegisterCollection(new Uri(uri), getCollection(collectionNode));
                            xqe.SetExternalVariable(new QName("", var), new XdmAtomicValue(uri));
                        }
                        else
                        {
                            // Supply a document URI.
                            // We exploit the fact that the short name of the document is
                            // always the same as the file name in these tests. With one exception!
                            if (sourceName == "Char010D")
                            {
                                sourceName = "0x010D";
                            }
                            String uri = "file:///" + testSuiteDir + "/TestSources/" + sourceName + ".xml";
                            xqe.SetExternalVariable(new QName("", var), new XdmAtomicValue(uri));
                        }
                    }
                }

                // Supply the default collection if required

                XdmNode defaultCollection = getChildElement(testCase, defaultCollectionNT);
                if (defaultCollection != null)
                {
                    String sourceName = defaultCollection.StringValue;
                    XPathSelector xpe = findCollection.Load();
                    xpe.SetVariable(new QName("", "param"), new XdmAtomicValue(sourceName));
                    xpe.ContextItem = catalog;
                    XdmNode collectionNode = (XdmNode)xpe.EvaluateSingle();
                    if (collectionNode == null)
                    {
                        log.WriteLine("*** Collection " + sourceName + " not found");
                    }
                    processor.RegisterCollection(null, getCollection(collectionNode));
                }

                // Supply any external variables defined as the result of a separate query

                IEnumerator ev = testCase.EnumerateAxis(XdmAxis.Child, inputQueryNT);
                while (ev.MoveNext())
                {
                    XdmNode inputQuery = (XdmNode)ev.Current;

                    String fileName = inputQuery.GetAttributeValue(nameAtt);
                    String subQueryPath = testSuiteDir + "/Queries/XQuery/" + filePath + fileName + ".xq";
                    XQueryCompiler subCompiler = processor.NewXQueryCompiler();
                    compiler.BaseUri = new Uri(subQueryPath).ToString();
                    FileStream subStream = new FileStream(subQueryPath, FileMode.Open, FileAccess.Read, FileShare.Read);
                    XdmValue value = subCompiler.Compile(subStream).Load().Evaluate();
                    String var = inputQuery.GetAttributeValue(variableAtt);
                    xqe.SetExternalVariable(new QName("", var), value);
                }

                // Supply the context item if required

                IEnumerator ci = testCase.EnumerateAxis(XdmAxis.Child, contextItemNT);
                while (ci.MoveNext())
                {
                    XdmNode file = (XdmNode)ci.Current;

                    String sourceName = file.StringValue;
                    if (!sourceDocs.ContainsKey(sourceName))
                    {
                        XdmNode doc = buildSource(catalog, builder, sourceName);
                        sourceDocs.Add(sourceName, doc);
                    }
                    XdmNode sourceDoc = (XdmNode)sourceDocs[sourceName];
                    xqe.ContextItem = sourceDoc;
                }

                // Create a serializer for the output


                outputPath = saxonResultsDir + "/results.net/" + filePath + queryName + ".out";
                Serializer sr = new Serializer();
                try
                {
                    sr.SetOutputFile(outputPath);
                    sr.SetOutputProperty(new QName("", "method"), "xml");
                    sr.SetOutputProperty(new QName("", "omit-xml-declaration"), "yes");
                    sr.SetOutputProperty(new QName("", "indent"), "no");
                }
                catch (DynamicError)
                {
                    // probably means that no output directory exists, which is probably because
                    // an error is expected
                    outputPath = saxonResultsDir + "/results.net/" + filePath + queryName + ".out";
                    sr.SetOutputFile(outputPath);
                }

                // Finally, run the query

                try
                {
                    xqe.Run(sr);
                }
                catch (DynamicError e)
                {
                    log.WriteLine(e.Message);
                    QName code = e.ErrorCode;
                    if (code != null && code.LocalName != null)
                    {
                        errorCode = code.LocalName;
                    }
                    else
                    {
                        errorCode = "ErrYYYYY";
                    }
                }
                catch (Exception e2)
                {
                    log.WriteLine("Unexpected exception: " + e2.Message);
                    log.WriteLine(e2.StackTrace);
                    errorCode = "CRASH!!!";
                }
            }

            // Compare actual results with expected results

            if (errorCode != null)
            {
                // query returned an error at compile time or run-time, check this was expected

                string expectedError = "";
                bool matched = false;
                IEnumerator en = testCase.EnumerateAxis(XdmAxis.Child, expectedErrorNT);
                while (en.MoveNext())
                {
                    XdmNode error = (XdmNode)en.Current;
                    String expectedErrorCode = error.StringValue;
                    expectedError += (expectedErrorCode + " ");
                    if (expectedErrorCode.Equals(errorCode))
                    {
                        matched = true;
                        feedback.Feedback(passed++, failed, total);
                        log.WriteLine("Error " + errorCode + " as expected");
                        results.WriteLine("<test-case name='" + testName + "' result='pass'/>");
                        break;
                    }
                }
                if (!matched)
                {
                    if (expectedError.Equals(""))
                    {
                        feedback.Feedback(passed, failed++, total);
                        log.WriteLine("Error " + errorCode + ", expected success");
                        results.WriteLine("<test-case name='" + testName + "' result='fail' comment='error " + errorCode + ", expected success'/>");
                        results.WriteLine("<--" + filePath + queryName + "-->");
                    }
                    else
                    {
                        feedback.Feedback(passed++, failed, total);
                        log.WriteLine("Error " + errorCode + ", expected " + expectedError);
                        results.WriteLine("<test-case name='" + testName + "' result='pass' comment='error " + errorCode + ", expected " + expectedError + "'/>");
                        results.WriteLine("<--" + filePath + queryName + "-->");
                    }
                }

            }
            else
            {
                // query returned no error

                bool matched = false;
                String diag = "";
                IEnumerator en = testCase.EnumerateAxis(XdmAxis.Child, outputFileNT);
                while (en.MoveNext())
                {
                    XdmNode outputFile = (XdmNode)en.Current;
                    String fileName = testSuiteDir + "/ExpectedTestResults/" + filePath + outputFile.StringValue;
                    String comparator = outputFile.GetAttributeValue(compareAtt);
                    if (comparator.Equals("Inspect"))
                    {
                        matched = true;
                        feedback.Feedback(passed++, failed, total);
                        results.WriteLine("<test-case name='" + testName + "' result='inspect'/>");
                        results.WriteLine("<--" + filePath + queryName + "-->");
                        break;
                    }
                    else
                    {
                        String comparison = fileComparer.compare(outputPath, fileName, comparator);
                        matched = (comparison == "OK" || comparison.StartsWith("#"));
                        if (matched)
                        {
                            feedback.Feedback(passed++, failed, total);
                            results.WriteLine("<test-case name='" + testName + "' result='pass'/>");
                            diag = diag + ("<!-- " + comparison + " -->\n");
                            break;
                        }
                    }
                }

                if (!matched)
                {
                    string expectedError = "";
                    IEnumerator ee = testCase.EnumerateAxis(XdmAxis.Child, expectedErrorNT);
                    while (ee.MoveNext())
                    {
                        XdmNode error = (XdmNode)ee.Current;
                        String expectedErrorCode = error.StringValue;
                        expectedError += (expectedErrorCode + " ");
                    }

                    if (expectedError.Equals(""))
                    {
                        feedback.Feedback(passed, failed++, total);
                        log.WriteLine("Results differ from expected results");
                        results.WriteLine("<test-case name='" + testName + "' result='fail'/>");
                        results.WriteLine("<--" + filePath + queryName + "-->");
                    }
                    else
                    {
                        feedback.Feedback(passed, failed++, total);
                        log.WriteLine("Error " + expectedError + "expected but not reported");
                        results.WriteLine("<test-case name='" + testName + "' result='fail' comment='expected error " + expectedError + "not reported'/>");
                        results.WriteLine("<--" + filePath + queryName + "-->");
                    }
                }
            }
        }

        results.WriteLine("</test-suite-result>");
        results.Close();
        log.Close();

    }

    /**
     * Construct source object. This method allows subclassing e.g. to build a DOM or XOM source.
     * @param xml
     * @return
     * @throws XPathException
     */

    protected XdmNode buildSource(XdmNode catalog, DocumentBuilder builder, String sourceName)
    {

        // Find the source element in the catalog

        XPathSelector xps = findSourcePath.Load();
        xps.SetVariable(new QName("", "param"), new XdmAtomicValue(sourceName));
        xps.ContextItem = catalog;
        XdmNode source = (XdmNode)xps.EvaluateSingle();

        // decide whether schema validation is needed

        bool validate = source.GetAttributeValue(new QName("", "schema")) != null;
        if (validate)
        {
            builder.SchemaValidationMode = SchemaValidationMode.Strict;
        }
        else
        {
            builder.SchemaValidationMode = SchemaValidationMode.None;
        }

        // build the document tree from the source file

        string filename = testSuiteDir + "/" + source.GetAttributeValue(new QName("", "FileName"));
        if (source == null)
        {
            throw new ArgumentException("Source " + sourceName + " not found in catalog");
        }
        return builder.Build(new Uri(filename));
    }


    private void outputDiscretionaryItems()
    {
        results.WriteLine("  <discretionary-items/>");
    }


    private IList getCollection(XdmNode collectionNode)
    {
        ArrayList list = new ArrayList(10);
        IEnumerator e = collectionNode.EnumerateAxis(
            XdmAxis.Child, new QName(testURI, "input-document"));
        while (e.MoveNext())
        {
            XdmNode node = (XdmNode)e.Current;
            list.Add(new Uri(testSuiteDir + "/TestSources/" + node.StringValue + ".xml"));
        }
        return list;
    }

    // Implementation of IQueryResolver used to locate library modules

    private class XqtsModuleResolver : IQueryResolver
    {

        private XdmNode testCase;
        private XPathExecutable findModule;

        public XqtsModuleResolver(XdmNode testCase, XPathExecutable findModule)
        {
            this.testCase = testCase;
            this.findModule = findModule;
        }

        public Uri[] GetModules(String moduleUri, Uri baseUri, String[] locationHints)
        {
            XPathSelector xps = findModule.Load();
            xps.SetVariable(new QName("", "testcase"), testCase);
            xps.SetVariable(new QName("", "moduleuri"), new XdmAtomicValue(moduleUri));
            ArrayList uris = new ArrayList();
            foreach (XdmItem i in xps) {
                uris.Add(new Uri((String)((XdmAtomicValue)i).Value));
            }
            return (Uri[])uris.ToArray(typeof(Uri));
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
    }




}


