using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Xml;
using Saxon.Api;

namespace TestRunner
{
         /**
         * This class runs the W3C XML Schema Test Suite, driven from the test catalog.
         */
        public class SchemaTestSuiteDriver {

            public static String testNS = "http://www.w3.org/XML/2004/xml-schema-test-suite/";
            /**
             * Run the testsuite using Saxon.
             *
             * @param args Array of parameters passed to the application
             * via the command line.
             */
 
            String testSuiteDir;
            IFeedbackListener feedback;
        
            bool onwards = false;

            StreamWriter results;
            QName xlinkHref;

            private XdmNode getChildElement(XdmNode parent, QName child)
            {
                IEnumerator e = parent.EnumerateAxis(XdmAxis.Child, child);
                return e.MoveNext() ? (XdmNode)e.Current : null;
            }

            public void setFeedbackListener(IFeedbackListener f)
            {
                feedback = f;
            }

            private XdmNode getLinkedDocument(XdmNode element, Processor processor, bool validate)
            {
                String href = element.GetAttributeValue(xlinkHref);
                DocumentBuilder builder = processor.NewDocumentBuilder();
                Uri target = new Uri(element.BaseUri, href);
                builder.IsLineNumbering = true;
                if (validate) {
                    builder.SchemaValidationMode = SchemaValidationMode.Strict;
                }
                return builder.Build(target);
            }


            /**
             * Run the tests
             * @param args command line arguments
             * @throws SAXException
             * @throws ParserConfigurationException
             * @throws XPathException
             * @throws IOException
             * @throws URISyntaxException
             */

            public void go(String[] args) {
                if (args.Length == 0 || args[0] == "-?")
                {
                    Console.WriteLine("SchemaTestSuiteDriver testDir [-w] [-onwards] -c:contributor? -s:setName? -g:groupName?");
                }
                Processor processor = new Processor(true);
                Console.WriteLine("Testing Saxon " + processor.ProductVersion);
                                
                testSuiteDir = args[0];
                if (testSuiteDir.EndsWith("/"))
                {
                    testSuiteDir = testSuiteDir.Substring(0, testSuiteDir.Length - 1);
                }
                String testSetPattern = null;   // TODO use a regex
                String testGroupPattern = null;
                String contributor = null;
                Hashtable exceptions = new Hashtable();

                for (int i=1; i<args.Length; i++) {
                    if (args[i] == ("-w")) {
                        //showWarnings = true;
                    } else if (args[i] == ("-onwards")) {
                        onwards = true;
                    } else if (args[i].StartsWith("-c:")) {
                        contributor = args[i].Substring(3);
                    } else if (args[i].StartsWith("-s:")) {
                        testSetPattern = args[i].Substring(3);
                    } else if (args[i].StartsWith("-g:")) {
                        testGroupPattern = args[i].Substring(3);
                    } else if (args[i] == "-?") {
                        Console.WriteLine("Usage: SchemaTestSuiteDriver testDir [-w] [-s:testSetPattern] [-g:testGroupPattern]");
                    }
                }

                int total = 39700;
                int passed = 0;
                int failed = 0;

                try {

                    xlinkHref = new QName("xlink", "http://www.w3.org/1999/xlink", "href");

                    QName testCaseNT = new QName("", "", "testcase");
                    QName commentNT = new QName("", "", "comment");

                    QName testSetRefNT = new QName(testNS, "testSetRef");
                    QName testGroupNT = new QName(testNS, "testGroup");
                    QName testSetNT = new QName(testNS, "testSet");
                    QName schemaTestNT = new QName(testNS, "schemaTest");
                    QName instanceTestNT = new QName(testNS, "instanceTest");
                    QName schemaDocumentNT = new QName(testNS, "schemaDocument");
                    QName instanceDocumentNT = new QName(testNS, "instanceDocument");
                    QName expectedNT = new QName(testNS, "expected");
                    QName currentNT = new QName(testNS, "current");

                    QName validityAtt = new QName("", "", "validity");
                    QName nameAtt = new QName("", "", "name");
                    QName contributorAtt = new QName("", "", "contributor");
                    QName setAtt = new QName("", "", "set");
                    QName groupAtt = new QName("", "", "group");
                    QName statusAtt = new QName("", "", "status");
                    QName bugzillaAtt = new QName("", "", "bugzilla");
                    QName targetNamespaceAtt = new QName("", "", "targetNamespace");
                    QName schemaVersion = new QName("saxon", "http://saxon.sf.net/", "schemaVersion");


                    DocumentBuilder builder = processor.NewDocumentBuilder();
                    builder.BaseUri = new Uri(testSuiteDir + "/");
                    XdmNode catalog = builder.Build(
                            new FileStream(testSuiteDir + "/suite.xml", FileMode.Open, FileAccess.Read, FileShare.Read));

                    results = new StreamWriter(testSuiteDir + "/saxon/SaxonResults"
                                + processor.ProductVersion + "n.xml");

                    results.Write("<testSuiteResults xmlns='" + testNS + "' xmlns:saxon='http://saxon.sf.net/' " +
                            "suite='TS_2006' " +
                            "processor='Saxon-SA (Java) 8.8++' submitDate='2007-01-05' publicationPermission='public'>\n");

                    XdmNode exceptionsDoc = builder.Build(
                            new FileStream(testSuiteDir + "/saxon/exceptions.xml", 
                                FileMode.Open, FileAccess.Read, FileShare.Read));

                  
                    IEnumerator exceptionTestCases = exceptionsDoc.EnumerateAxis(XdmAxis.Descendant, new QName("", "testcase"));
                    while (exceptionTestCases.MoveNext()) {
                        XdmNode testCase = (XdmNode)exceptionTestCases.Current;
                        String set = testCase.GetAttributeValue(setAtt);
                        String group = testCase.GetAttributeValue(groupAtt);
                        String comment = getChildElement(testCase, commentNT).StringValue;
                        exceptions[set + "#" + group] = comment;
                    }

                    IEnumerator testSets = catalog.EnumerateAxis(XdmAxis.Descendant, testSetRefNT);
                    while (testSets.MoveNext()) {

                        XdmNode testSetRef = (XdmNode)testSets.Current;
                        XdmNode testSetDoc = getLinkedDocument(testSetRef, processor, false);
                        XdmNode testSetElement = getChildElement(testSetDoc, testSetNT);

                        if (testSetElement == null) {
                            feedback.Message("test set doc has no TestSet child: " + testSetDoc.BaseUri, true);
                            continue;
                        }

                        String testSetName = testSetElement.GetAttributeValue(nameAtt);
                        if (testSetPattern != null && !testSetName.StartsWith(testSetPattern)) {
                            continue;
                        }
                        if (contributor != null && contributor != testSetElement.GetAttributeValue(contributorAtt)) {
                            continue;
                        }

                        bool needs11 = (testSetElement.GetAttributeValue(schemaVersion) == "1.1"); 

                        IEnumerator testGroups = testSetElement.EnumerateAxis(XdmAxis.Child, testGroupNT);
                        while (testGroups.MoveNext()) {
                            XdmNode testGroup = (XdmNode)testGroups.Current;
                            
                            String testGroupName = testGroup.GetAttributeValue(nameAtt);
                            String exception = (String)exceptions[testSetName + "#" + testGroupName];

                            if (testGroupPattern != null && !testGroupName.StartsWith(testGroupPattern)) {
                                continue;
                            }
                            Console.WriteLine("TEST SET " + testSetName + " GROUP " + testGroupName, false);
                            if (onwards) {
                                testGroupPattern = null;
                                testSetPattern = null;
                            }
                            Processor testConfig = new Processor(true);
                            if (needs11)
                            {
                                testConfig.SetProperty("http://saxon.sf.net/feature/xsd-version", "1.1");
                            }
                            SchemaManager schemaManager = testConfig.SchemaManager;
                            

                            //testConfig.setHostLanguage(Configuration.XML_SCHEMA);
                            testConfig.SetProperty("http://saxon.sf.net/feature/validation-warnings", "true");
                            IEnumerator schemaTests = testGroup.EnumerateAxis(XdmAxis.Child, schemaTestNT);
                            bool schemaQueried = false;
                            String bugzillaRef = null;

                            while (schemaTests.MoveNext()) {
                                XdmNode schemaTest = (XdmNode)schemaTests.Current;
                                if (schemaTest == null) {
                                    break;
                                }
                                bugzillaRef = null;
                                String testName = schemaTest.GetAttributeValue(nameAtt);
                                if (exception != null) {
                                    results.Write("<testResult set='" + testSetName +
                                            "' group='" + testGroupName +
                                            "' test='" + testName +
                                            "' validity='notKnown' saxon:outcome='notRun' saxon:comment='" + exception +
                                            "'/>\n");
                                    continue;
                                }
                                bool queried = false;
                                XdmNode statusElement = getChildElement(schemaTest, currentNT);
                                if (statusElement != null) {
                                    String status = statusElement.GetAttributeValue(statusAtt);
                                    queried = ("queried" == status);
                                    bugzillaRef = statusElement.GetAttributeValue(bugzillaAtt);
                                }
                                if (queried) {
                                    schemaQueried = true;
                                }
                                Console.WriteLine("TEST SCHEMA " + testName + (queried ? " (queried)" : ""));
                                bool success = true;
                                IEnumerator schemata = schemaTest.EnumerateAxis(XdmAxis.Child, schemaDocumentNT);
                                while (schemata.MoveNext()) {
                                    XdmNode schemaDocumentRef = (XdmNode)schemata.Current;
                                    if (schemaDocumentRef == null) {
                                        break;
                                    }
                                    Console.WriteLine("Loading schema at " + schemaDocumentRef.GetAttributeValue(xlinkHref));
                                    XdmNode schemaDoc = getLinkedDocument(schemaDocumentRef, testConfig, false);
                                    IEnumerator schemaDocKids = schemaDoc.EnumerateAxis(XdmAxis.Child);
                                    XdmNode schemaElement = null;
                                    while (schemaDocKids.MoveNext())
                                    {
                                        schemaElement = (XdmNode)schemaDocKids.Current;
                                        if (schemaElement.NodeKind == XmlNodeType.Element)
                                        {
                                            break;
                                        }
                                    }
                                    String targetNamespace = schemaElement.GetAttributeValue(targetNamespaceAtt);
                                    //if (targetNamespace != null && schemaManager. isSchemaAvailable(targetNamespace)) {
                                        // do nothing
                                        // TODO: this is the only way I can get MS additional test addB132 to work.
                                        // It's not ideal: addSchemaSource() ought to be a no-op if the schema components
                                        // are already loaded, but in fact recompiling the imported schema document on its
                                        // own is losing the substitution group membership that was defined in the
                                        // importing document.
                                    //} else {
                                    IList errorList = new ArrayList();
                                    schemaManager.ErrorList = errorList;
                                    try
                                    {
                                        schemaManager.Compile(schemaDoc);
                                    }
                                    catch (Exception e)
                                    {
                                        if (errorList.Count == 0)
                                        {
                                            feedback.Message("In " + testName + ", exception thrown but no errors in ErrorList\n", true);
                                            results.Write("<!--" + e.Message + "-->");
                                            success = false;
                                        }
                                    }
                                    for (int i = 0; i < errorList.Count; i++)
                                    {
                                        if (errorList[i] is StaticError)
                                        {
                                            StaticError err = (StaticError)errorList[i];
                                            if (!err.IsWarning)
                                            {
                                                success = false;
                                                break;
                                            }
                                        }
                                        else
                                        {
                                            feedback.Message("In " + testName + " wrong kind of error!" + errorList[i].GetType() + "\n", true);
                                        }
                                    }
                                }
                                XdmNode expected = getChildElement(schemaTest, expectedNT);
                                bool expectedSuccess = expected==null ||
                                        expected.GetAttributeValue(validityAtt) == "valid";
                                if (success == expectedSuccess)
                                {
                                    passed++;
                                }
                                else
                                {
                                    failed++;
                                }
                                feedback.Feedback(passed, failed, total);
                                results.Write("<testResult set='" + testSetName +
                                        "' group='" + testGroupName +
                                        "' test='" + testName +
                                        "' validity='" + (success ? "valid" : "invalid" ) +
                                        (queried ? "' saxon:queried='true' saxon:bugzilla='" + bugzillaRef : "") +
                                        "' saxon:outcome='" + (success==expectedSuccess ? "same" : "different") +
                                        "'/>\n");
                            }
                            IEnumerator instanceTests = testGroup.EnumerateAxis(XdmAxis.Child, instanceTestNT);
                            while (instanceTests.MoveNext()) {
                                XdmNode instanceTest = (XdmNode)instanceTests.Current;
                                String testName = instanceTest.GetAttributeValue(nameAtt);

                                if (exception != null) {
                                    results.Write("<testResult set='" + testSetName +
                                            "' group='" + testGroupName +
                                            "' test='" + testName +
                                            "' validity='notKnown' saxon:outcome='notRun' saxon:comment='" + exception +
                                            "'/>\n");
                                    continue;
                                }

                                bool queried = false;
                                XdmNode statusElement = getChildElement(instanceTest, currentNT);
                                if (statusElement != null) {
                                    String status = statusElement.GetAttributeValue(statusAtt);
                                    queried = ("queried" == status);
                                    String instanceBug = statusElement.GetAttributeValue(bugzillaAtt);
                                    if (instanceBug != null) {
                                        bugzillaRef = instanceBug;
                                    }
                                }
                                queried |= schemaQueried;

                                Console.WriteLine("TEST INSTANCE " + testName + (queried ? " (queried)" : ""));

                                XdmNode instanceDocument = getChildElement(instanceTest, instanceDocumentNT);

                                bool success = true;
                                try
                                {
                                    XdmNode instanceDoc = getLinkedDocument(instanceDocument, testConfig, true);
                                }
                                catch (Exception)
                                {
                                    success = false;
                                }
                                
                                XdmNode expected = getChildElement(instanceTest, expectedNT);
                                bool expectedSuccess = expected==null ||
                                        expected.GetAttributeValue(validityAtt) == "valid";
                                if (success == expectedSuccess)
                                {
                                    passed++;
                                }
                                else
                                {
                                    failed++;
                                }
                                feedback.Feedback(passed, failed, total);
                                results.Write("<testResult set='" + testSetName +
                                        "' group='" + testGroupName +
                                        "' test='" + testName +
                                        "' validity='" + (success ? "valid" : "invalid" ) +
                                        (queried ? "' saxon:queried='true' saxon:bugzilla='" + bugzillaRef : "") +
                                        "' saxon:outcome='" + (success==expectedSuccess ? "same" : "different") +
                                        "'/>\n");

                            }
                        }
                    }

                    results.Write("</testSuiteResults>");
                    results.Close();

                } catch (Exception e) {
                    feedback.Message("Test failed: " + e.Message, true);
                }
            }

            protected String getResultDirectoryName() {
                return "SaxonResults";
            }

            protected bool isExcluded(String testName) {
                return false;
            }


        }


    }

