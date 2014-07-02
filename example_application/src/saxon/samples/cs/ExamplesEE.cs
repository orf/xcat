using System;
using System.IO;
using System.Collections;
using System.Xml;
using System.Net;
using Saxon.Api;


namespace SaxonEE
{
    class ExamplesEE
    {
        /// <summary>
        /// Run Saxon XSLT and XQuery sample applications for Saxon Enterprise Edition on .NET
        /// </summary>
        /// <param name="argv">
        /// <para>Options:</para>
        /// <list>
        /// <item>-test:testname  run a specific test</item>
        /// <item>-dir:samplesdir directory containing the sample data files (default %SAXON_HOME%/samples)</item>
        /// <item>-ask:yes|no     indicates whether to prompt for confirmation after each test (default yes)</item>
        /// </list>
        /// </param>


        public static void Main(String[] argv)
        {

            Example[] examples = {
                new XPathSimple(),
                new XPathVariables(),
                new XPathUndeclaredVariables(),
                new XPathWithStaticError(),
                new XPathWithDynamicError(),
                new XsltSimple1(),
                new XsltSimple2(),
                new XsltSimple3(),
                new XsltStripSpace(),
                new XsltReuseExecutable(),
                new XsltReuseTransformer(),
                new XsltFilterChain(),
                new XsltDomToDom(),
                new XsltXdmToXdm(),
                new XsltXdmElementToXdm(),
                new XsltUsingSourceResolver(),
                new XsltSettingOutputProperties(),
                new XsltDisplayingErrors(),
                new XsltCapturingErrors(),
                new XsltCapturingMessages(),
                new XsltProcessingInstruction(),
                new XsltShowingLineNumbers(),
                new XsltMultipleOutput(),
                new XsltUsingResultHandler(),
                new XsltUsingIdFunction(),
                new XsltUsingRegisteredCollection(),
                new XsltUsingDirectoryCollection(),
                new XsltExtensibility(),
                new XsltIntegratedExtension(),
                new XQueryToStream(),
                new XQueryToAtomicValue(),
                new XQueryToSequence(),
                new XQueryToDom(),
                new XQueryToXdm(),
                new XQueryCallFunction(),
                new XQueryFromXmlReader(),
                new XQueryMultiModule(),
                new XQueryToSerializedSequence(),
                new XQueryUsingParameter(),
                new XQueryExtensibility(),
                new XQueryUpdate(),
                new Validate(),
                new XQueryTryCatch(),
                new XQuerySchemaAware(),
                new XPathSchemaAware(),
                new XsltStreamDoc()
            };

            Boolean ask = true;
            String test = "all";

            String samplesPath = null;
            Uri samplesDir;

            foreach (String s in argv)
            {
                if (s.StartsWith("-test:"))
                {
                    test = s.Substring(6);
                }
                else if (s.StartsWith("-dir:"))
                {
                    samplesPath = s.Substring(5);
                }
                else if (s == "-ask:yes")
                {
                    // no action
                }
                else if (s == "-ask:no")
                {
                    ask = false;
                }
                else if (s == "-?")
                {
                    Console.WriteLine("ExamplesEE -dir:samples -test:testname -ask:yes|no");
                }
                else
                {
                    Console.WriteLine("Unrecognized Argument: " + s);
                    return;
                }
            }
            if (samplesPath != null)
            {
                if (samplesPath.StartsWith("file:///"))
                {
                    samplesPath = samplesPath.Substring(8);
                }
                else if (samplesPath.StartsWith("file:/"))
                {
                    samplesPath = samplesPath.Substring(6);
                }

            }
            else
            {
                String home = Environment.GetEnvironmentVariable("SAXON_HOME");
                if (home == null)
                {
                    Console.WriteLine("No input directory supplied, and SAXON_HOME is not set");
                    return;
                }
                else
                {
                    if (!(home.EndsWith("/") || home.EndsWith("\\")))
                    {
                        home = home + "/";
                    }
                    samplesPath = home + "samples/";
                }
            }

            if (!(samplesPath.EndsWith("/") || samplesPath.EndsWith("\\")))
            {
                samplesPath = samplesPath + "/";
            }

            if (!File.Exists(samplesPath + "data/books.xml"))
            {
                Console.WriteLine("Supplied samples directory " + samplesPath + " does not contain the Saxon sample data files");
                return;
            }

            try
            {
                samplesDir = new Uri(samplesPath);
            }
            catch
            {
                Console.WriteLine("Invalid URI for samples directory: " + samplesPath);
                return;
            }

            foreach (Example ex in examples)
            {
                if (test == "all" || test == ex.testName)
                {
                    Console.WriteLine("\n\n===== " + ex.testName + " =======\n");
                    try
                    {
                        ex.run(samplesDir);
                    }
                    catch (Saxon.Api.StaticError se)
                    {
                        Console.WriteLine("Test failed with static error " + se.ErrorCode.LocalName + ": " + se.Message);
                    }
                    catch (Saxon.Api.DynamicError de)
                    {
                        Console.WriteLine("Test failed with dynamic error " + de.ErrorCode.LocalName + ": " + de.Message);
                    }
                    catch (Exception exc)
                    {
                        Console.WriteLine("Test failed unexpectedly (" + exc.GetType() + "): " + exc.Message);
                        Console.WriteLine(exc.StackTrace);
                    }
                    if (ask)
                    {
                        Console.WriteLine("\n\nContinue? - type (Y(es)/N(o)/A(ll))");
                        String answer = Console.ReadLine();
                        if (answer == "N" || answer == "n")
                        {
                            break;
                        }
                        else if (answer == "A" || answer == "a")
                        {
                            ask = false;
                        }
                    }
                }
            }
            Console.WriteLine("\n==== done! ====");
        }
    }

    ///<summary>
    /// Each of the example programs is implemented as a subclass of the abstract class Example
    ///</summary> 


    public abstract class Example
    {
        /// <summary>
        /// Read-only property: the name of the test example
        /// </summary>
        public abstract String testName { get; }
        /// <summary>
        /// Entry point for running the example
        /// </summary>
        public abstract void run(Uri samplesDir);
    }

    /// <summary>
    /// XPath expression selecting from a source document supplied as a URI
    /// </summary>

    public class XPathSimple : Example
    {

        public override String testName
        {
            get { return "XPathSimple"; }
        }

        /// <summary>
        /// Run a transformation: simplest possible script
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create an XPath compiler
            XPathCompiler xpath = processor.NewXPathCompiler();

            // Enable caching, so each expression is only compiled once
            xpath.Caching = true;

            // Compile and evaluate some XPath expressions
            foreach (XdmItem item in xpath.Evaluate("//ITEM", input))
            {
                Console.WriteLine("TITLE: " + xpath.EvaluateSingle("string(TITLE)", item));
                Console.WriteLine("PRICE: " + xpath.EvaluateSingle("string(PRICE)", item));
            }
        }
    }

    /// <summary>
    /// XPath expression using variables (and no source document)
    /// </summary>

    public class XPathVariables : Example
    {

        public override String testName
        {
            get { return "XPathVariables"; }
        }

        /// <summary>
        /// Run a transformation: simplest possible script
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XPath expression.
            XPathCompiler compiler = processor.NewXPathCompiler();
            compiler.DeclareVariable(new QName("", "a"));
            compiler.DeclareVariable(new QName("", "b"));
            XPathSelector selector = compiler.Compile("$a + $b").Load();

            // Set the values of the variables
            selector.SetVariable(new QName("", "a"), new XdmAtomicValue(2));
            selector.SetVariable(new QName("", "b"), new XdmAtomicValue(3));

            // Evaluate the XPath expression
            Console.WriteLine(selector.EvaluateSingle().ToString());
        }
    }

    /// <summary>
    /// XPath expression using variables without explicit declaration
    /// </summary>

    public class XPathUndeclaredVariables : Example
    {

        public override String testName
        {
            get { return "XPathUndeclaredVariables"; }
        }

        /// <summary>
        /// Execute an XPath expression containing undeclared variables
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XPath expression.
            XPathCompiler compiler = processor.NewXPathCompiler();
            compiler.AllowUndeclaredVariables = true;
            XPathExecutable expression = compiler.Compile("$a + $b");
            XPathSelector selector = expression.Load();

            // Set the values of the variables
            IEnumerator vars = expression.EnumerateExternalVariables();
            while (vars.MoveNext())
            {
                selector.SetVariable((QName)vars.Current, new XdmAtomicValue(10));
            }

            // Evaluate the XPath expression
            Console.WriteLine(selector.EvaluateSingle().ToString());
        }
    }

    /// <summary>
    /// XPath expression throwing a static error
    /// </summary>

    public class XPathWithStaticError : Example
    {

        public override String testName
        {
            get { return "XPathWithStaticError"; }
        }

        /// <summary>
        /// Execute an XPath expression that throws a dynamic error, and catch the error
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XPath expression.
            XPathCompiler compiler = processor.NewXPathCompiler();
            compiler.AllowUndeclaredVariables = true;
            XPathExecutable expression = compiler.Compile("1 + unknown()");
            XPathSelector selector = expression.Load();

            // Evaluate the XPath expression
            Console.WriteLine(selector.EvaluateSingle().ToString());
        }
    }

    /// <summary>
    /// XPath expression throwing a dynamic error
    /// </summary>

    public class XPathWithDynamicError : Example
    {

        public override String testName
        {
            get { return "XPathWithDynamicError"; }
        }

        /// <summary>
        /// Execute an XPath expression that throws a dynamic error
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XPath expression.
            XPathCompiler compiler = processor.NewXPathCompiler();
            compiler.AllowUndeclaredVariables = true;
            XPathExecutable expression = compiler.Compile("$a gt $b");
            XPathSelector selector = expression.Load();

            // Set the values of the variables
            selector.SetVariable(new QName("", "a"), new XdmAtomicValue(10));
            selector.SetVariable(new QName("", "b"), new XdmAtomicValue("Paris"));

            // Evaluate the XPath expression
            Console.WriteLine(selector.EvaluateSingle().ToString());
        }
    }

    /// <summary>
    /// XSLT 2.0 transformation with source document and stylesheet supplied as URIs
    /// </summary>

    public class XsltSimple1 : Example
    {

        public override String testName
        {
            get { return "XsltSimple1"; }
        }

        /// <summary>
        /// Run a transformation: simplest possible script
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/books.xsl")).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer, with output to the standard output stream
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML and serialize the result document
            transformer.Run(serializer);
        }
    }

    /// <summary>
    /// Run a transformation, sending the serialized output to a file
    /// </summary>

    public class XsltSimple2 : Example
    {

        public override String testName
        {
            get { return "XsltSimple2"; }
        }

        /// <summary>
        /// Run the transformation, sending the serialized output to a file
        /// </summary>


        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/identity.xsl")).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer
            String outfile = "OutputFromXsltSimple2.xml";
            Serializer serializer = new Serializer();
            serializer.SetOutputStream(new FileStream(outfile, FileMode.Create, FileAccess.Write));

            // Transform the source XML to System.out.
            transformer.Run(serializer);

            Console.WriteLine("\nOutput written to " + outfile + "\n");
        }
    }

    /// <summary>
    /// XSLT 2.0 transformation with source document and stylesheet supplied as URIs
    /// </summary>

    public class XsltSimple3 : Example
    {

        public override String testName
        {
            get { return "XsltSimple3"; }
        }

        /// <summary>
        /// Run a transformation: supply input as a file
        /// </summary>

        public override void run(Uri samplesDir)
        {
            if (samplesDir.Scheme != Uri.UriSchemeFile)
            {
                Console.WriteLine("Supplied URI must be a file directory");
            }
            String dir = samplesDir.AbsolutePath;
            String sourceFile = dir + "data/books.xml";
            String styleFile = dir + "styles/books.xsl";

            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document

            DocumentBuilder builder = processor.NewDocumentBuilder();
            builder.BaseUri = new Uri(samplesDir, "data/books.xml");

            XdmNode input = builder.Build(File.OpenRead(sourceFile));

            // Create a transformer for the stylesheet.
            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = new Uri(samplesDir, "styles/books.xsl");
            XsltTransformer transformer = compiler.Compile(File.OpenRead(styleFile)).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer, with output to the standard output stream
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML and serialize the result document
            transformer.Run(serializer);
        }
    }


    /// <summary>
    /// XSLT 2.0 transformation showing stripping of whitespace controlled by the stylesheet
    /// </summary>

    public class XsltStripSpace : Example
    {

        public override String testName
        {
            get { return "XsltStripSpace"; }
        }

        /// <summary>
        /// Run a transformation: simplest possible script
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();

            // Load the source document
            DocumentBuilder builder = processor.NewDocumentBuilder();
            builder.BaseUri = samplesDir;

            String doc = "<doc>  <a>  <b>text</b>  </a>  <a/>  </doc>";
            MemoryStream ms = new MemoryStream();
            StreamWriter tw = new StreamWriter(ms);
            tw.Write(doc);
            tw.Flush();
            Stream instr = new MemoryStream(ms.GetBuffer(), 0, (int)ms.Length);
            XdmNode input = builder.Build(instr);

            // Create a transformer for the stylesheet.
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>" +
                "<xsl:strip-space elements='*'/>" +
                "<xsl:template match='/'>" +
                "  <xsl:copy-of select='.'/>" +
                "</xsl:template>" +
                "</xsl:stylesheet>";

            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = samplesDir;
            XsltTransformer transformer = compiler.Compile(new XmlTextReader(new StringReader(stylesheet))).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML to System.out.
            transformer.Run(serializer);
        }
    }


    /// <summary>
    /// Run a transformation, compiling the stylesheet once and using it to transform two different source documents
    /// </summary>

    public class XsltReuseExecutable : Example
    {

        public override String testName
        {
            get { return "XsltReuseExecutable"; }
        }

        /// <summary>
        /// Show that a stylesheet can be compiled once (into an XsltExecutable) and run many times
        /// </summary>
        /// <param name="fileNames">
        /// 1. first source document
        /// 2. second source document
        /// 3. stylesheet used to transform both documents
        /// </param>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create a compiled stylesheet
            XsltExecutable templates = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/summarize.xsl"));

            // Note: we could actually use the same XsltTransformer in this case.
            // But in principle, the two transformations could be done in parallel in separate threads.

            String sourceFile1 = "data/books.xml";
            String sourceFile2 = "data/othello.xml";

            // Do the first transformation
            Console.WriteLine("\n\n----- transform of " + sourceFile1 + " -----");
            XsltTransformer transformer1 = templates.Load();
            transformer1.InitialContextNode = processor.NewDocumentBuilder().Build(new Uri(samplesDir, sourceFile1));
            transformer1.Run(new Serializer());     // default destination is Console.Out

            // Do the second transformation
            Console.WriteLine("\n\n----- transform of " + sourceFile2 + " -----");
            XsltTransformer transformer2 = templates.Load();
            transformer2.InitialContextNode = processor.NewDocumentBuilder().Build(new Uri(samplesDir, sourceFile2));
            transformer2.Run(new Serializer());     // default destination is Console.Out    
        }
    }

    /// <summary>
    /// Show that the XsltTransformer is serially reusable; run a transformation twice using the same stylesheet
    /// and the same input document but with different parameters.
    /// </summary>

    public class XsltReuseTransformer : Example
    {

        public override String testName
        {
            get { return "XsltReuseTransformer"; }
        }

        /// <summary>
        /// Show that the XsltTransformer is serially reusable (we run it twice with different parameter settings)
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document, building a tree
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Compile the stylesheet
            XsltExecutable exec = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/summarize.xsl"));

            // Create a transformer 
            XsltTransformer transformer = exec.Load();

            // Run it once        
            transformer.SetParameter(new QName("", "", "include-attributes"), new XdmAtomicValue(false));
            transformer.InitialContextNode = input;
            XdmDestination results = new XdmDestination();
            transformer.Run(results);
            Console.WriteLine("1: " + results.XdmNode.OuterXml);

            // Run it again        
            transformer.SetParameter(new QName("", "", "include-attributes"), new XdmAtomicValue(true));
            transformer.InitialContextNode = input;
            results.Reset();
            transformer.Run(results);
            Console.WriteLine("2: " + results.XdmNode.OuterXml);
        }
    }

    /// <summary>
    /// Run a sequence of transformations in a pipeline, each one acting as a filter
    /// </summary>

    public class XsltFilterChain : Example
    {

        public override String testName
        {
            get { return "XsltFilterChain"; }
        }

        /// <summary>
        /// Run the test
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create a compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Compile all three stylesheets
            XsltTransformer transformer1 = compiler.Compile(new Uri(samplesDir, "styles/identity.xsl")).Load();
            XsltTransformer transformer2 = compiler.Compile(new Uri(samplesDir, "styles/books.xsl")).Load();
            XsltTransformer transformer3 = compiler.Compile(new Uri(samplesDir, "styles/summarize.xsl")).Load();

            // Now run them in series
            transformer1.InitialContextNode = input;
            XdmDestination results1 = new XdmDestination();
            transformer1.Run(results1);
            //Console.WriteLine("After phase 1:");
            //Console.WriteLine(results1.XdmNode.OuterXml);

            transformer2.InitialContextNode = results1.XdmNode;
            XdmDestination results2 = new XdmDestination();
            transformer2.Run(results2);
            //Console.WriteLine("After phase 2:");
            //Console.WriteLine(results2.XdmNode.OuterXml);

            transformer3.InitialContextNode = results2.XdmNode;
            //TextWriterDestination results3 = new TextWriterDestination(new XmlTextWriter(Console.Out));
            XdmDestination results3 = new XdmDestination();
            transformer3.Run(results3);
            Console.WriteLine("After phase 3:");
            Console.WriteLine(results3.XdmNode.OuterXml);
        }
    }

    /// <summary>
    /// Transform from an XDM tree to an XDM tree
    /// </summary>

    public class XsltXdmToXdm : Example
    {

        public override String testName
        {
            get { return "XsltXdmToXdm"; }
        }

        /// <summary>
        /// Transform from an XDM tree to an XDM tree
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create a compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Compile the stylesheet
            XsltTransformer transformer = compiler.Compile(new Uri(samplesDir, "styles/summarize.xsl")).Load();

            // Run the transformation
            transformer.InitialContextNode = input;
            XdmDestination result = new XdmDestination();
            transformer.Run(result);

            // Serialize the result so we can see that it worked
            StringWriter sw = new StringWriter();
            result.XdmNode.WriteTo(new XmlTextWriter(sw));
            Console.WriteLine(sw.ToString());

            // Note: we don't do 
            //   result.XdmNode.WriteTo(new XmlTextWriter(Console.Out));
            // because that results in the Console.out stream being closed, 
            // with subsequent attempts to write to it being rejected.
        }
    }

    /// <summary>
    /// Run an XSLT transformation from an Xdm tree, starting at a node that is not the document node
    /// </summary>

    public class XsltXdmElementToXdm : Example
    {

        public override String testName
        {
            get { return "XsltXdmElementToXdm"; }
        }

        /// <summary>
        /// Run an XSLT transformation from an Xdm tree, starting at a node that is not the document node
        /// </summary>
        /// <param name="fileNames">
        /// 1. The source document
        /// 2. The stylesheet
        /// </param>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/othello.xml"));

            // Navigate to the first grandchild
            XPathSelector eval = processor.NewXPathCompiler().Compile("/PLAY/FM[1]").Load();
            eval.ContextItem = input;
            input = (XdmNode)eval.EvaluateSingle();

            // Create an XSLT compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Compile the stylesheet
            XsltTransformer transformer = compiler.Compile(new Uri(samplesDir, "styles/summarize.xsl")).Load();

            // Run the transformation
            transformer.InitialContextNode = input;
            XdmDestination result = new XdmDestination();
            transformer.Run(result);

            // Serialize the result so we can see that it worked
            Console.WriteLine(result.XdmNode.OuterXml);
        }
    }

    /// <summary>
    /// Run a transformation from a DOM (System.Xml.Document) input to a DOM output
    /// </summary>

    public class XsltDomToDom : Example
    {

        public override String testName
        {
            get { return "XsltDomToDom"; }
        }

        /// <summary>
        /// Run a transformation from a DOM (System.Xml.Document) input to a DOM output
        /// </summary>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document (in practice, it would already exist as a DOM)
            XmlDocument doc = new XmlDocument();
            doc.Load(new XmlTextReader(samplesDir.AbsolutePath + "data/othello.xml"));
            XdmNode input = processor.NewDocumentBuilder().Wrap(doc);

            // Create a compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Compile the stylesheet
            XsltTransformer transformer = compiler.Compile(new Uri(samplesDir, "styles/summarize.xsl")).Load();

            // Run the transformation
            transformer.InitialContextNode = input;
            DomDestination result = new DomDestination();
            transformer.Run(result);

            // Serialize the result so we can see that it worked
            Console.WriteLine(result.XmlDocument.OuterXml);
        }
    }


    /// <summary>
    /// Run a transformation driven by an xml-stylesheet processing instruction in the source document
    /// </summary>

    public class XsltProcessingInstruction : Example
    {

        public override string testName
        {
            get { return "XsltProcessingInstruction"; }
        }

        /// <summary>
        /// Run a transformation driven by an xml-stylesheet processing instruction in the source document
        /// </summary>
        /// <param name="fileNames">
        /// 1. The source document
        /// </param>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();
            XsltExecutable exec;

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));
            //Console.WriteLine("=============== source document ===============");
            //Console.WriteLine(input.OuterXml);
            //Console.WriteLine("=========== end of source document ============");

            // Navigate to the xml-stylesheet processing instruction having the pseudo-attribute type=text/xsl;
            // then extract the value of the href pseudo-attribute if present

            String path = @"/processing-instruction(xml-stylesheet)[matches(.,'type\s*=\s*[''""]text/xsl[''""]')]" +
                    @"/replace(., '.*?href\s*=\s*[''""](.*?)[''""].*', '$1')";

            XPathSelector eval = processor.NewXPathCompiler().Compile(path).Load();
            eval.ContextItem = input;
            XdmAtomicValue hrefval = (XdmAtomicValue)eval.EvaluateSingle();
            String href = (hrefval == null ? null : hrefval.ToString());

            if (href == null || href == "")
            {
                Console.WriteLine("No suitable xml-stylesheet processing instruction found");
                return;

            }
            else if (href[0] == '#')
            {

                // The stylesheet is embedded in the source document and identified by a URI of the form "#id"

                Console.WriteLine("Locating embedded stylesheet with href = " + href);
                String idpath = "id('" + href.Substring(1) + "')";
                eval = processor.NewXPathCompiler().Compile(idpath).Load();
                eval.ContextItem = input;
                XdmNode node = (XdmNode)eval.EvaluateSingle();
                if (node == null)
                {
                    Console.WriteLine("No element found with ID " + href.Substring(1));
                    return;
                }
                exec = processor.NewXsltCompiler().Compile(node);

            }
            else
            {

                // The stylesheet is in an external document

                Console.WriteLine("Locating stylesheet at uri = " + new Uri(input.BaseUri, href));

                // Fetch and compile the referenced stylesheet
                exec = processor.NewXsltCompiler().Compile(new Uri(input.BaseUri, href.ToString()));
            }

            // Create a transformer 
            XsltTransformer transformer = exec.Load();

            // Run it       
            transformer.InitialContextNode = input;
            XdmDestination results = new XdmDestination();
            transformer.Run(results);
            Console.WriteLine("1: " + results.XdmNode.OuterXml);

        }
    }

    /// <summary>
    /// Run an XSLT transformation setting serialization properties from the calling application
    /// </summary>

    public class XsltSettingOutputProperties : Example
    {

        public override string testName
        {
            get { return "XsltSettingOutputProperties"; }
        }

        /// <summary>
        /// Run an XSLT transformation setting serialization properties from the calling application
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/books.xml"));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/summarize.xsl")).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer, with output to the standard output stream
            Serializer serializer = new Serializer();
            serializer.SetOutputProperty(Serializer.METHOD, "xml");
            serializer.SetOutputProperty(Serializer.INDENT, "no");
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML and serialize the result document
            transformer.Run(serializer);
        }

    }

    /// <summary>
    /// Run an XSLT transformation making use of an XmlResolver to resolve URIs at document build time, at stylesheet compile time 
    /// and at transformation run-time
    /// </summary>

    public class XsltUsingSourceResolver : Example
    {

        public override string testName
        {
            get { return "XsltUsingSourceResolver"; }
        }

        /// <summary>
        /// Run an XSLT transformation making use of an XmlResolver to resolve URIs both at compile time and at run-time
        /// </summary>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            DocumentBuilder builder = processor.NewDocumentBuilder();
            UserXmlResolver buildTimeResolver = new UserXmlResolver();
            buildTimeResolver.Message = "** Calling build-time XmlResolver: ";
            builder.XmlResolver = buildTimeResolver;
            builder.BaseUri = samplesDir;

            String doc = "<!DOCTYPE doc [<!ENTITY e SYSTEM 'flamingo.txt'>]><doc>&e;</doc>";
            MemoryStream ms = new MemoryStream();
            StreamWriter tw = new StreamWriter(ms);
            tw.Write(doc);
            tw.Flush();
            Stream instr = new MemoryStream(ms.GetBuffer(), 0, (int)ms.Length);
            XdmNode input = builder.Build(instr);

            // Create a transformer for the stylesheet.
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>" +
                "<xsl:import href='empty.xslt'/>" +
                "<xsl:template match='/'>" +
                "<out note=\"{doc('heron.txt')}\" ><xsl:copy-of select='.'/></out>" +
                "</xsl:template>" +
                "</xsl:stylesheet>";

            XsltCompiler compiler = processor.NewXsltCompiler();
            UserXmlResolver compileTimeResolver = new UserXmlResolver();
            compileTimeResolver.Message = "** Calling compile-time XmlResolver: ";
            compiler.XmlResolver = compileTimeResolver;
            compiler.BaseUri = samplesDir;
            XsltTransformer transformer = compiler.Compile(new XmlTextReader(new StringReader(stylesheet))).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Set the user-written XmlResolver
            UserXmlResolver runTimeResolver = new UserXmlResolver();
            runTimeResolver.Message = "** Calling transformation-time XmlResolver: ";
            transformer.InputXmlResolver = runTimeResolver;

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML to System.out.
            transformer.Run(serializer);

        }
    }

    /// <summary>
    /// Run an XSLT transformation displaying compile-time errors to the console
    /// </summary>

    public class XsltDisplayingErrors : Example
    {

        public override string testName
        {
            get { return "XsltDisplayingErrors"; }
        }

        /// <summary>
        /// Run an XSLT transformation displaying compile-time errors to the console
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XSLT Compiler
            XsltCompiler compiler = processor.NewXsltCompiler();


            // Define a stylesheet containing errors
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>\n" +
                "<xsl:template name='eee:template'>\n" +
                "  <xsl:value-of select='32'/>\n" +
                "</xsl:template>\n" +
                "<xsl:template name='main'>\n" +
                "  <xsl:value-of select='$var'/>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";


            // Attempt to compile the stylesheet and display the errors
            try
            {
                compiler.BaseUri = new Uri("http://localhost/stylesheet");
                compiler.Compile(new XmlTextReader(new StringReader(stylesheet)));
                Console.WriteLine("Stylesheet compilation succeeded");
            }
            catch (Exception)
            {
                Console.WriteLine("Stylesheet compilation failed");
            }


        }
    }

    /// <summary>
    /// Run an XSLT transformation capturing compile-time errors within the application
    /// </summary>

    public class XsltCapturingErrors : Example
    {

        public override string testName
        {
            get { return "XsltCapturingErrors"; }
        }

        /// <summary>
        /// Run an XSLT transformation capturing compile-time errors within the application
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XSLT Compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Create a list to hold the error information
            compiler.ErrorList = new ArrayList();

            // Define a stylesheet containing errors
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>\n" +
                "<xsl:template name='fff:template'>\n" +
                "  <xsl:value-of select='32'/>\n" +
                "</xsl:template>\n" +
                "<xsl:template name='main'>\n" +
                "  <xsl:value-of select='$var'/>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";


            // Attempt to compile the stylesheet and display the errors
            try
            {
                compiler.BaseUri = new Uri("http://localhost/stylesheet");
                compiler.Compile(new StringReader(stylesheet));
                Console.WriteLine("Stylesheet compilation succeeded");
            }
            catch (Exception)
            {
                Console.WriteLine("Stylesheet compilation failed with " + compiler.ErrorList.Count + " errors");
                foreach (StaticError error in compiler.ErrorList)
                {
                    Console.WriteLine("At line " + error.LineNumber + ": " + error.Message);
                }
            }
        }
    }

    /// <summary>
    /// Run an XSLT transformation capturing run-time messages within the application
    /// </summary>

    public class XsltCapturingMessages : Example
    {

        public override string testName
        {
            get { return "XsltCapturingMessages"; }
        }

        /// <summary>
        /// Run an XSLT transformation capturing run-time messages within the application
        /// </summary>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Create the XSLT Compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Define a stylesheet that generates messages
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>\n" +
                "<xsl:template name='main'>\n" +
                "  <xsl:message><a>starting</a></xsl:message>\n" +
                "  <out><xsl:value-of select='current-date()'/></out>\n" +
                "  <xsl:message><a>finishing</a></xsl:message>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";

            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));


            // Create a transformer for the stylesheet.
            XsltTransformer transformer = exec.Load();

            // Set the name of the initial template
            transformer.InitialTemplate = new QName("", "main");

            // Create a Listener to which messages will be written
            transformer.MessageListener = new UserMessageListener();

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML to System.out.
            transformer.Run(serializer);
        }

    }

    ///
    /// Example user-written message listener
    ///

    public class UserMessageListener : IMessageListener
    {

        public void Message(XdmNode content, bool terminate, IXmlLocation location)
        {
            Console.Out.WriteLine("MESSAGE terminate=" + (terminate ? "yes" : "no") + " at " + DateTime.Now);
            Console.Out.WriteLine("From instruction at line " + location.LineNumber +
                    " of " + location.BaseUri);
            Console.Out.WriteLine(">>" + content.StringValue);
        }
    }

    /// <summary>
    /// Run an XSLT transformation showing source line numbers
    /// </summary>

    public class XsltShowingLineNumbers : Example
    {

        public override string testName
        {
            get { return "XsltShowingLineNumbers"; }
        }

        /// <summary>
        /// Run an XSLT transformation capturing run-time messages within the application
        /// </summary>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Ask for the JAXP parser to be used (or not to be used, if false)
            processor.SetProperty("http://saxon.sf.net/feature/preferJaxpParser", "false");

            // Load the source document
            DocumentBuilder builder = processor.NewDocumentBuilder();
            builder.IsLineNumbering = true;
            XdmNode input = builder.Build(new Uri(samplesDir, "data/othello.xml"));

            // Create the XSLT Compiler
            XsltCompiler compiler = processor.NewXsltCompiler();

            // Define a stylesheet that shows line numbers of source elements
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0' xmlns:saxon='http://saxon.sf.net/'>\n" +
                "<xsl:template match='/'>\n" +
                "<out>\n" +
                "  <xsl:for-each select='//ACT'>\n" +
                "  <out><xsl:value-of select='saxon:line-number(.)'/></out>\n" +
                "  </xsl:for-each>\n" +
                "</out>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";

            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));


            // Create a transformer for the stylesheet.
            XsltTransformer transformer = exec.Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML to System.out.
            transformer.Run(serializer);
        }

    }

    /// <summary>
    /// Run an XSLT transformation producing multiple output documents
    /// </summary>

    public class XsltMultipleOutput : Example
    {

        public override string testName
        {
            get { return "XsltMultipleOutput"; }
        }

        /// <summary>
        /// Run an XSLT transformation producing multiple output documents
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();
            processor.SetProperty("http://saxon.sf.net/feature/timing", "true");

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/othello.xml"));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new Uri(samplesDir, "styles/play.xsl")).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Set the required stylesheet parameter
            transformer.SetParameter(new QName("", "", "dir"), new XdmAtomicValue(samplesDir.ToString() + "play"));

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);

            // Transform the source XML to System.out.
            transformer.Run(serializer);

        }

    }


    /// <summary>
    /// Run an XSLT transformation using the id() function, with DTD validation
    /// </summary>

    public class XsltUsingIdFunction : Example
    {

        public override string testName
        {
            get { return "XsltUsingIdFunction"; }
        }

        /// <summary>
        /// Run an XSLT transformation using the id() function, with DTD validation
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance
            Processor processor = new Processor();

            // Load the source document. The Microsoft .NET parser does not report attributes of type ID. The only
            // way to use the function is therefore (a) to use a different parser, or (b) to use xml:id instead. We
            // choose the latter course.

            String doc = "<!DOCTYPE table [" +
                "<!ELEMENT table (row*)>" +
                "<!ELEMENT row EMPTY>" +
                "<!ATTLIST row xml:id ID #REQUIRED>" +
                "<!ATTLIST row value CDATA #REQUIRED>]>" +
                "<table><row xml:id='A123' value='green'/><row xml:id='Z789' value='blue'/></table>";

            DocumentBuilder builder = processor.NewDocumentBuilder();
            builder.DtdValidation = true;
            builder.BaseUri = samplesDir;
            MemoryStream ms = new MemoryStream();
            StreamWriter tw = new StreamWriter(ms);
            tw.Write(doc);
            tw.Flush();
            Stream instr = new MemoryStream(ms.GetBuffer(), 0, (int)ms.Length);
            XdmNode input = builder.Build(instr);

            // Define a stylesheet that uses the id() function
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>\n" +
                "<xsl:template match='/'>\n" +
                "  <xsl:copy-of select=\"id('Z789')\"/>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";

            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));

            //Create a transformer for the stylesheet
            XsltTransformer transformer = exec.Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            //Set the destination
            XdmDestination results = new XdmDestination();

            // Transform the XML
            transformer.Run(results);

            // Show the result
            Console.WriteLine(results.XdmNode.ToString());

        }

    }

    /// <summary>
    /// Show a transformation using a user-written result document handler. This example
    /// captures each of the result documents in a DOM, and creates a Hashtable that indexes
    /// the DOM trees according to their absolute URI. On completion, it writes all the DOMs
    /// to the standard output.
    /// </summary>

    public class XsltUsingResultHandler : Example
    {

        public override string testName
        {
            get { return "XsltUsingResultHandler"; }
        }

        /// <summary>
        /// Show a transformation using a user-written result document handler. This example
        /// captures each of the result documents in a DOM, and creates a Hashtable that indexes
        /// the DOM trees according to their absolute URI. On completion, it writes all the DOMs
        /// to the standard output.
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/othello.xml"));

            // Define a stylesheet that splits the document up
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>\n" +
                "<xsl:template match='/'>\n" +
                "  <xsl:for-each select='//ACT'>\n" +
                "    <xsl:result-document href='{position()}.xml'>\n" +
                "      <xsl:copy-of select='TITLE'/>\n" +
                "    </xsl:result-document>\n" +
                "  </xsl:for-each>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";

            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = exec.Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Establish the result document handler
            Hashtable results = new Hashtable();
            transformer.ResultDocumentHandler = new UserResultDocumentHandler(results);

            // Transform the source XML to a NullDestination (because we only want the secondary result files).
            transformer.Run(new NullDestination());

            // Process the captured DOM results
            foreach (DictionaryEntry entry in results)
            {
                string uri = (string)entry.Key;
                Console.WriteLine("\nResult File " + uri);
                DomDestination dom = (DomDestination)results[uri];
                Console.Write(dom.XmlDocument.OuterXml);
            }

        }

    }

    /// <summary>
    /// Show a transformation using a registered collection
    /// </summary>

    public class XsltUsingRegisteredCollection : Example
    {

        public override string testName
        {
            get { return "XsltUsingRegisteredCollection"; }
        }

        /// <summary>
        /// Show a transformation using a registered collection
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/othello.xml"));

            // Define a stylesheet that splits the document up
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>\n" +
                "<xsl:template name='main'>\n" +
                " <out>\n" +
                "  <xsl:for-each select=\"collection('http://www.example.org/my-collection')\">\n" +
                "    <document uri='{document-uri(.)}' nodes='{count(//*)}'/>\n" +
                "  </xsl:for-each><zzz/>\n" +
                "  <xsl:for-each select=\"collection('http://www.example.org/my-collection')\">\n" +
                "    <document uri='{document-uri(.)}' nodes='{count(//*)}'/>\n" +
                "  </xsl:for-each>\n" +
                " </out>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";

            Uri[] documentList = new Uri[2];
            documentList[0] = new Uri(samplesDir, "data/othello.xml");
            documentList[1] = new Uri(samplesDir, "data/books.xml");
            processor.RegisterCollection(new Uri("http://www.example.org/my-collection"), documentList);

            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = exec.Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialTemplate = new QName("", "main");

            //Set the destination
            XdmDestination results = new XdmDestination();

            // Transform the XML
            transformer.Run(results);

            // Show the result
            Console.WriteLine(results.XdmNode.ToString());

        }
    }

    /// <summary>
    /// Show a transformation using a registered collection
    /// </summary>

    public class XsltUsingDirectoryCollection : Example
    {

        public override string testName
        {
            get { return "XsltUsingDirectoryCollection"; }
        }

        /// <summary>
        /// Show a transformation using a collection that maps to a directory
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Create a Processor instance.
            Processor processor = new Processor();

            // Load the source document
            XdmNode input = processor.NewDocumentBuilder().Build(new Uri(samplesDir, "data/othello.xml"));

            // Define a stylesheet that splits the document up
            String stylesheet =
                "<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='2.0'>\n" +
                "<xsl:template name='main'>\n" +
                " <out>\n" +
                "  <xsl:for-each select=\"collection('" + samplesDir + "?recurse=yes;select=*.xml;on-error=warning')\">\n" +
                "    <document uri='{document-uri(.)}' nodes='{count(//*)}'/>\n" +
                "  </xsl:for-each><zzz/>\n" +
                " </out>\n" +
                "</xsl:template>\n" +
                "</xsl:stylesheet>";


            XsltCompiler compiler = processor.NewXsltCompiler();
            compiler.BaseUri = new Uri("http://localhost/stylesheet");
            XsltExecutable exec = compiler.Compile(new StringReader(stylesheet));

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = exec.Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialTemplate = new QName("", "main");

            //Set the destination
            XdmDestination results = new XdmDestination();

            // Transform the XML
            transformer.Run(results);

            // Show the result
            Console.WriteLine(results.XdmNode.ToString());

        }

    }

    /// <summary>
    /// Show a transformation using calls to extension functions
    /// </summary>

    public class XsltExtensibility : Example
    {

        public override string testName
        {
            get { return "XsltExtensibility"; }
        }
        /// <summary>
        /// Demonstrate XSLT extensibility using user-written extension functions
        /// </summary>
        /// <remarks>Note: If SamplesExtensions is compiled to a different assembly than ExamplesEE, use 
        /// the namespace URI clitype:SampleExtensions.SampleExtensions?asm=ASSEMBLY_NAME_HERE
        /// </remarks>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Identify the Processor version
            Console.WriteLine(processor.ProductVersion);

            // Set diagnostics
            //processor.SetProperty("http://saxon.sf.net/feature/trace-external-functions", "true");

            // Create the stylesheet
            String s = @"<xsl:transform version='2.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'" +
                @" xmlns:ext='clitype:SampleExtensions.SampleExtensions?asm=ExamplesEE' " +
                @" xmlns:tz='clitype:System.TimeZone' " +
                @" xmlns:math='http://example.math.co.uk/demo' " +
                @" xmlns:env='http://example.env.co.uk/demo' " +
                @" exclude-result-prefixes='ext math env tz'> " +
                @" <xsl:param name='timezone' required='yes'/> " +
                @" <xsl:template match='/'> " +
                @" <out addition='{ext:add(2,2)}' " +
                @" average='{ext:average((1,2,3,4,5,6))}' " +
                @" firstchild='{ext:nameOfFirstChild(.)}' " +
                @" timezone='{tz:StandardName($timezone)}' " +
                @" sqrt2='{math:sqrt(2.0e0)}' " +
                @" defaultNamespace='{env:defaultNamespace()}' " +
                @" sqrtEmpty='{math:sqrt(())}'> " +
                @" <xsl:copy-of select='ext:FirstChild((//ITEM)[1])'/> " +
                @" <defaultNS value='{env:defaultNamespace()}' xsl:xpath-default-namespace='http://default.namespace.com/' /> " +
                @" <combine1><xsl:sequence select='ext:combine(ext:FirstChild((//ITEM)[1]), count(*))'/></combine1> " +
                @" <combine2><xsl:sequence select='ext:combine((//TITLE)[1], (//AUTHOR)[1])'/></combine2> " +
                @" </out> " +
                @" </xsl:template></xsl:transform>";

            // Register the integrated extension functions math:sqrt and env:defaultNamespace

            processor.RegisterExtensionFunction(new Sqrt());
            processor.RegisterExtensionFunction(new DefaultNamespace());

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new StringReader(s)).Load();

            // Load the source document (must be a wrapper around an XmlDocument for this test)
            XmlDocument doc = new XmlDocument();
            doc.Load(new XmlTextReader(samplesDir.AbsolutePath + "data/books.xml"));
            XdmNode input = processor.NewDocumentBuilder().Wrap(doc);

            // Set the root node of the source document to be the initial context node
            transformer.InitialContextNode = input;

            // Supply a parameter
            transformer.SetParameter(new QName("", "timezone"),
                      XdmAtomicValue.WrapExternalObject(TimeZone.CurrentTimeZone));

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);
            serializer.SetOutputProperty(Serializer.INDENT, "yes");

            // Transform the source XML to System.out.
            transformer.Run(serializer);
        }

    }

    /// <summary>
    /// Show a transformation using calls to extension functions
    /// </summary>

    public class XsltIntegratedExtension : Example
    {

        public override string testName
        {
            get { return "XsltIntegratedExtension"; }
        }

        /// <summary>
        /// Show a transformation using calls to extension functions
        /// </summary>

        public override void run(Uri samplesDir)
        {

            // Create a Processor instance.
            Processor processor = new Processor();

            // Identify the Processor version
            Console.WriteLine(processor.ProductVersion);

            // Set diagnostics
            //processor.SetProperty("http://saxon.sf.net/feature/trace-external-functions", "true");

            // Create the stylesheet
            String s = @"<xsl:transform version='2.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'" +
                @" xmlns:math='http://example.math.co.uk/demo'> " +
                @" <xsl:template name='go'> " +
                @" <out sqrt2='{math:sqrt(2.0e0)}' " +
                @" sqrtEmpty='{math:sqrt(())}'/> " +
                @" </xsl:template></xsl:transform>";

            // Register the integrated extension function math:sqrt

            processor.RegisterExtensionFunction(new Sqrt());

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new StringReader(s)).Load();

            // Set the root node of the source document to be the initial context node
            transformer.InitialTemplate = new QName("go");

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);
            serializer.SetOutputProperty(Serializer.INDENT, "yes");

            // Transform the source XML to System.out.
            transformer.Run(serializer);
        }

    }

    /// <summary>
    /// A try-catch expression in the query, a feature of XQuery 3.0
    /// to the C# application
    /// </summary>

    public class XQueryTryCatch : Example
    {

        public override string testName
        {
            get { return "XQueryTryCatch"; }
        }

        /// <summary>
        /// Show a query producing a single atomic value as its result and returning the value
        /// to the C# application
        /// </summary>

        public override void run(Uri samplesDir)
        {

            String query = "xquery version '1.1'; try {doc('book.xml')}catch * {\"XQuery 1.1 catch clause - file not found.\"}";
            Processor processor = new Processor();

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.XQueryLanguageVersion = "1.1";
            XQueryExecutable exp = compiler.Compile(query);
            XQueryEvaluator eval = exp.Load();
            Serializer qout = new Serializer();
            eval.Run(qout);
        }

    }

    /// <summary>
    /// Example extension function to compute a square root.
    /// </summary>

    public class Sqrt : ExtensionFunctionDefinition
    {
        public override QName FunctionName
        {
            get
            {
                return new QName("http://example.math.co.uk/demo", "sqrt");
            }
        }

        public override int MinimumNumberOfArguments
        {
            get
            {
                return 1;
            }
        }

        public override int MaximumNumberOfArguments
        {
            get
            {
                return 1;
            }
        }

        public override XdmSequenceType[] ArgumentTypes
        {
            get
            {
                return new XdmSequenceType[]{
                    new XdmSequenceType(XdmAtomicType.BuiltInAtomicType(QName.XS_DOUBLE), '?')
                };
            }
        }

        public override XdmSequenceType ResultType(XdmSequenceType[] ArgumentTypes)
        {
            return new XdmSequenceType(XdmAtomicType.BuiltInAtomicType(QName.XS_DOUBLE), '?');
        }

        public override bool TrustResultType
        {
            get
            {
                return true;
            }
        }


        public override ExtensionFunctionCall MakeFunctionCall()
        {
            return new SqrtCall();
        }
    }

    internal class SqrtCall : ExtensionFunctionCall
    {
        public override IXdmEnumerator Call(IXdmEnumerator[] arguments, DynamicContext context)
        {
            Boolean exists = arguments[0].MoveNext();
            if (exists)
            {
                XdmAtomicValue arg = (XdmAtomicValue)arguments[0].Current;
                double val = (double)arg.Value;
                double sqrt = System.Math.Sqrt(val);
                XdmAtomicValue result = new XdmAtomicValue(sqrt);
                return (IXdmEnumerator)result.GetEnumerator();
            }
            else
            {
                return EmptyEnumerator.INSTANCE;
            }
        }

    }

    /// <summary>
    /// Example extension function to return the default namespace from the static context
    /// </summary>

    public class DefaultNamespace : ExtensionFunctionDefinition
    {
        public override QName FunctionName
        {
            get
            {
                return new QName("http://example.env.co.uk/demo", "defaultNamespace");
            }
        }

        public override int MinimumNumberOfArguments
        {
            get
            {
                return 0;
            }
        }

        public override int MaximumNumberOfArguments
        {
            get
            {
                return 0;
            }
        }

        public override XdmSequenceType[] ArgumentTypes
        {
            get
            {
                return new XdmSequenceType[] { };
            }
        }

        public override bool DependsOnFocus
        {
            get
            {
                return true;
                // actually it depends on the static context rather than the focus; but returning true is necessary
                // to avoid the call being extracted to a global variable.
            }
        }

        public override XdmSequenceType ResultType(XdmSequenceType[] ArgumentTypes)
        {
            return new XdmSequenceType(XdmAtomicType.BuiltInAtomicType(QName.XS_STRING), '?');
        }

        public override bool TrustResultType
        {
            get
            {
                return true;
            }
        }


        public override ExtensionFunctionCall MakeFunctionCall()
        {
            return new DefaultNamespaceCall();
        }
    }

    internal class DefaultNamespaceCall : ExtensionFunctionCall
    {
        private string defaultNamespace;

        public override void SupplyStaticContext(StaticContext context)
        {
            defaultNamespace = context.GetNamespaceForPrefix("");
        }

        public override IXdmEnumerator Call(IXdmEnumerator[] arguments, DynamicContext context)
        {
            if (defaultNamespace != null)
            {
                return (IXdmEnumerator)new XdmAtomicValue(defaultNamespace).GetEnumerator();
            }
            else
            {
                return EmptyEnumerator.INSTANCE;
            }
        }

    }

    /// <summary>
    /// Show a query producing a document as its result and serializing this to a FileStream
    /// </summary>

    public class XQueryToStream : Example
    {

        public override string testName
        {
            get { return "XQueryToStream"; }
        }

        /// <summary>
        /// Show a query producing a document as its result and serializing this to a FileStream
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.BaseUri = samplesDir.ToString();
            compiler.DeclareNamespace("saxon", "http://saxon.sf.net/");
            XQueryExecutable exp = compiler.Compile("<saxon:example>{static-base-uri()}</saxon:example>");
            XQueryEvaluator eval = exp.Load();
            Serializer qout = new Serializer();
            qout.SetOutputProperty(Serializer.METHOD, "xml");
            qout.SetOutputProperty(Serializer.INDENT, "yes");
            qout.SetOutputProperty(Serializer.SAXON_INDENT_SPACES, "1");
            qout.SetOutputStream(new FileStream("testoutput.xml", FileMode.Create, FileAccess.Write));
            Console.WriteLine("Output written to testoutput.xml");
            eval.Run(qout);
        }

    }

    /// <summary>
    /// Show a query producing a single atomic value as its result and returning the value
    /// to the C# application
    /// </summary>

    public class XQueryToAtomicValue : Example
    {

        public override string testName
        {
            get { return "XQueryToAtomicValue"; }
        }

        /// <summary>
        /// Show a query producing a single atomic value as its result and returning the value
        /// to the C# application
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("avg(for $i in 1 to 10 return $i * $i)");
            XQueryEvaluator eval = exp.Load();
            XdmAtomicValue result = (XdmAtomicValue)eval.EvaluateSingle();
            Console.WriteLine("Result type: " + result.Value.GetType());
            Console.WriteLine("Result value: " + (decimal)result.Value);
        }

    }

    /// <summary>
    /// Show a query producing a DOM as its input and producing a DOM as its output
    /// </summary>

    public class XQueryToDom : Example
    {

        public override string testName
        {
            get { return "XQueryToDom"; }
        }

        /// <summary>
        /// Show a query producing a DOM as its input and producing a DOM as its output
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();

            XmlDocument input = new XmlDocument();
            input.Load(new Uri(samplesDir, "data/books.xml").ToString());
            XdmNode indoc = processor.NewDocumentBuilder().Build(new XmlNodeReader(input));

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("<doc>{reverse(/*/*)}</doc>");
            XQueryEvaluator eval = exp.Load();
            eval.ContextItem = indoc;
            DomDestination qout = new DomDestination();
            eval.Run(qout);
            XmlDocument outdoc = qout.XmlDocument;
            Console.WriteLine(outdoc.OuterXml);
        }

    }

    /// <summary>
    /// Show a query producing a Saxon tree as its input and producing a Saxon tree as its output
    /// </summary>

    public class XQueryToXdm : Example
    {

        public override string testName
        {
            get { return "XQueryToXdm"; }
        }

        /// <summary>
        /// Show a query producing a Saxon tree as its input and producing a Saxon tree as its output
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();

            DocumentBuilder loader = processor.NewDocumentBuilder();
            loader.BaseUri = new Uri(samplesDir, "data/books.xml");
            XdmNode indoc = loader.Build(loader.BaseUri);

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("<doc>{reverse(/*/*)}</doc>");
            XQueryEvaluator eval = exp.Load();
            eval.ContextItem = indoc;
            XdmDestination qout = new XdmDestination();
            eval.Run(qout);
            XdmNode outdoc = qout.XdmNode;
            Console.WriteLine(outdoc.OuterXml);
        }

    }

    /// <summary>
    /// Show a query making a direct call to a user-defined function defined in the query
    /// </summary>

    public class XQueryCallFunction : Example
    {

        public override string testName
        {
            get { return "XQueryCallFunction"; }
        }

        /// <summary>
        /// Show a direct call on a user-defined function defined within the query
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();

            XQueryCompiler qc = processor.NewXQueryCompiler();
            Uri uri = new Uri(samplesDir, "data/books.xml");
            XQueryExecutable exp1 = qc.Compile("declare namespace f='f.ns';" +
                   "declare variable $z := 1 + xs:integer(doc-available('" + uri.ToString() + "'));" +
                   "declare variable $p as xs:integer external;" +
                   "declare function f:t1($v1 as xs:integer) { " +
                   "   $v1 div $z + $p" +
                   "};" +
                   "10");
            XQueryEvaluator ev = exp1.Load();
            ev.SetExternalVariable(new QName("", "p"), new XdmAtomicValue(39));
            XdmValue v1 = new XdmAtomicValue(10);
            XdmValue result = ev.CallFunction(new QName("f.ns", "f:t1"), new XdmValue[] { v1 });
            Console.WriteLine("First result (expected 44): " + result.ToString());
            v1 = new XdmAtomicValue(20);
            result = ev.CallFunction(new QName("f.ns", "f:t1"), new XdmValue[] { v1 });
            Console.WriteLine("Second result (expected 49): " + result.ToString());
        }

    }



    /// <summary>
    /// Show a query producing a sequence as its result and returning the sequence
    /// to the C# application in the form of an iterator. For each item in the
    /// result, its string value is output.
    /// </summary>

    public class XQueryToSequence : Example
    {

        public override string testName
        {
            get { return "XQueryToSequence"; }
        }

        /// <summary>
        /// Show a query producing a sequence as its result and returning the sequence
        /// to the C# application in the form of an iterator. For each item in the
        /// result, its string value is output.
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("for $i in 1 to 10 return $i * $i");
            XQueryEvaluator eval = exp.Load();
            XdmValue value = eval.Evaluate();
            IEnumerator e = value.GetEnumerator();
            while (e.MoveNext())
            {
                XdmItem item = (XdmItem)e.Current;
                Console.WriteLine(item.ToString());
            }

        }

    }

    /// <summary>
    /// Show a query reading an input document using an XmlReader (the .NET XML parser)
    /// </summary>

    public class XQueryFromXmlReader : Example
    {

        public override string testName
        {
            get { return "XQueryFromXmlReader"; }
        }

        /// <summary>
        /// Show a query reading an input document using an XmlReader (the .NET XML parser)
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();

            String inputFileName = new Uri(samplesDir, "data/books.xml").ToString();
            XmlTextReader reader = new XmlTextReader(inputFileName,
                UriConnection.getReadableUriStream(new Uri(samplesDir, "data/books.xml")));
            //new FileStream(inputFileName, FileMode.Open, FileAccess.Read));
            reader.Normalization = true;

            // add a validating reader - not to perform validation, but to expand entity references
            XmlValidatingReader validator = new XmlValidatingReader(reader);
            validator.ValidationType = ValidationType.None;

            XdmNode doc = processor.NewDocumentBuilder().Build(validator);

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("/");
            XQueryEvaluator eval = exp.Load();
            eval.ContextItem = doc;
            Serializer qout = new Serializer();
            qout.SetOutputProperty(Serializer.METHOD, "xml");
            qout.SetOutputProperty(Serializer.INDENT, "yes");
            qout.SetOutputStream(new FileStream("testoutput2.xml", FileMode.Create, FileAccess.Write));
            eval.Run(qout);
        }

    }

    /// <summary>
    /// Show a query producing a sequence as its result and returning the sequence
    /// to the C# application in the form of an iterator. The sequence is then
    /// output by serializing each item individually, with each item on a new line.
    /// </summary>

    public class XQueryToSerializedSequence : Example
    {

        public override string testName
        {
            get { return "XQueryToSerializedSequence"; }
        }

        /// <summary>
        /// Show a query producing a sequence as its result and returning the sequence
        /// to the C# application in the form of an iterator. The sequence is then
        /// output by serializing each item individually, with each item on a new line.
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();
            String inputFileName = new Uri(samplesDir, "data/books.xml").ToString();
            //XmlTextReader reader = new XmlTextReader(inputFileName,
            //    new FileStream(inputFileName, FileMode.Open, FileAccess.Read));
            XmlTextReader reader = new XmlTextReader(inputFileName,
                UriConnection.getReadableUriStream(new Uri(samplesDir, "data/books.xml")));
            reader.Normalization = true;

            // add a validating reader - not to perform validation, but to expand entity references
            XmlValidatingReader validator = new XmlValidatingReader(reader);
            validator.ValidationType = ValidationType.None;

            XdmNode doc = processor.NewDocumentBuilder().Build(reader);
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile("//ISBN");

            XQueryEvaluator eval = exp.Load();
            eval.ContextItem = doc;

            foreach (XdmNode node in eval)
            {
                Console.WriteLine(node.OuterXml);
            }
        }

    }

    /// <summary>
    /// Show a query that takes a parameter (external variable) as input.
    /// The query produces a single atomic value as its result and returns the value
    /// to the C# application. 
    /// </summary>

    public class XQueryUsingParameter : Example
    {

        public override string testName
        {
            get { return "XQueryUsingParameter"; }
        }

        /// <summary>
        /// Show a query that takes a parameter (external variable) as input.
        /// The query produces a single atomic value as its result and returns the value
        /// to the C# application. 
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.DeclareNamespace("p", "http://saxon.sf.net/ns/p");
            XQueryExecutable exp = compiler.Compile(
                    "declare variable $p:in as xs:integer external; $p:in * $p:in");
            XQueryEvaluator eval = exp.Load();
            eval.SetExternalVariable(new QName("http://saxon.sf.net/ns/p", "p:in"), new XdmAtomicValue(12));
            XdmAtomicValue result = (XdmAtomicValue)eval.EvaluateSingle();
            Console.WriteLine("Result type: " + result.Value.GetType());
            Console.WriteLine("Result value: " + (long)result.Value);
        }

    }

    /// <summary>
    /// Show a query consisting of two modules, using a QueryResolver to resolve
    /// the "import module" declaration
    /// </summary>

    public class XQueryMultiModule : Example
    {

        public override string testName
        {
            get { return "XQueryMultiModule"; }
        }

        /// <summary>
        /// Show a query consisting of two modules, using a QueryResolver to resolve
        /// the "import module" declaration
        /// </summary>

        public override void run(Uri samplesDir)
        {

            String mod1 = "import module namespace m2 = 'http://www.example.com/module2';" +
                          "m2:square(3)";

            String mod2 = "module namespace m2 = 'http://www.example.com/module2';" +
                          "declare function m2:square($p) { $p * $p };";

            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();

            InlineModuleResolver resolver = new InlineModuleResolver();
            resolver.AddModule(new Uri("http://www.example.com/module2"), mod2);
            compiler.QueryResolver = resolver;
            XQueryExecutable exp = compiler.Compile(mod1);
            XQueryEvaluator eval = exp.Load();

            XdmAtomicValue result = (XdmAtomicValue)eval.EvaluateSingle();
            Console.WriteLine("Result type: " + result.Value.GetType());
            Console.WriteLine("Result value: " + (long)result.Value);
        }

        // A simple QueryResolver designed to show that the actual query
        // text can come from anywhere: in this case, the resolver maintains
        // a simple mapping of module URIs onto strings.

        public class InlineModuleResolver : IQueryResolver
        {

            private Hashtable modules = new Hashtable();

            public void AddModule(Uri moduleName, String moduleText)
            {
                modules.Add(moduleName, moduleText);
            }

            public Uri[] GetModules(String moduleUri, Uri baseUri, String[] locationHints)
            {
                Uri[] result = { new Uri(moduleUri) };
                return result;
            }

            public Object GetEntity(Uri absoluteUri)
            {
                return modules[absoluteUri];
            }
        }

    }

    /// <summary>
    /// Demonstrate XQuery extensibility using user-written extension functions
    /// </summary>

    public class XQueryExtensibility : Example
    {

        public override string testName
        {
            get { return "XQueryExtensibility"; }
        }

        /// <summary>
        /// Demonstrate XQuery extensibility using user-written extension functions
        /// </summary>
        /// <remarks>Note: If SamplesExtensions is compiled to a different assembly than ExamplesEE, use 
        /// the namespace URI clitype:SampleExtensions.SampleExtensions?asm=ASSEMBLY_NAME_HERE
        /// </remarks>

        public override void run(Uri samplesDir)
        {
            String query =
                "declare namespace ext = \"clitype:SampleExtensions.SampleExtensions?asm=ExamplesEE\";" +
                "<out>" +
                "  <addition>{ext:add(2,2)}</addition>" +
                "  <average>{ext:average((1,2,3,4,5,6))}</average>" +
                "  <language>{ext:hostLanguage()}</language>" +
                "</out>";

            Processor processor = new Processor();
            XQueryCompiler compiler = processor.NewXQueryCompiler();
            XQueryExecutable exp = compiler.Compile(query);
            XQueryEvaluator eval = exp.Load();
            Serializer qout = new Serializer();
            eval.Run(qout);
        }

    }

    /// <summary>
    /// Demonstrate XQuery Update
    /// </summary>

    public class XQueryUpdate : Example
    {

        public override string testName
        {
            get { return "SA-XQueryUpdate"; }
        }

        /// <summary>
        /// Demonstrate XQuery Update
        /// </summary>

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor(true);

            DocumentBuilder loader = processor.NewDocumentBuilder();
            loader.BaseUri = new Uri(samplesDir, "data/books.xml");
            loader.TreeModel = TreeModel.LinkedTree;
            XdmNode indoc = loader.Build(new Uri(samplesDir, "data/books.xml"));

            Console.Out.WriteLine("=========== BEFORE UPDATE ===========");

            Serializer serializer0 = new Serializer();
            serializer0.SetOutputProperty(Serializer.METHOD, "xml");
            serializer0.SetOutputProperty(Serializer.INDENT, "yes");
            serializer0.SetOutputWriter(Console.Out);
            processor.WriteXdmValue(indoc, serializer0);

            String query =
                "for $i in //PRICE return \n" +
                "replace value of node $i with $i - 0.05";

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.UpdatingEnabled = true;
            XQueryExecutable exp = compiler.Compile(query);
            XQueryEvaluator eval = exp.Load();
            eval.ContextItem = indoc;
            XdmNode[] updatedNodes = eval.RunUpdate();
            foreach (XdmNode root in updatedNodes)
            {
                Uri documentUri = root.DocumentUri;
                if (documentUri != null && documentUri.Scheme == "file")
                {
                    Stream stream = UriConnection.getWritableUriStream(documentUri);
                    Serializer serializer = new Serializer();
                    serializer.SetOutputProperty(Serializer.METHOD, "xml");
                    serializer.SetOutputProperty(Serializer.INDENT, "yes");
                    serializer.SetOutputStream(stream);
                    processor.WriteXdmValue(root, serializer);
                }
            }

            Console.Out.WriteLine("=========== AFTER UPDATE ===========");

            processor.WriteXdmValue(indoc, serializer0);
        }
    }

    /// <summary>
    /// A try-catch expression in the query, a feature of XQuery 3.0
    /// to the C# application
    /// </summary>

    public class XQuerySchemaAware : Example
    {

        public override string testName
        {
            get { return "XQuerySchemaAware"; }
        }

        public override void run(Uri samplesDir)
        {

            String query = "import schema default element namespace \"\" at \"" + samplesDir + "\\data\\books.xsd\";\n" +
                            "for $integer in (validate { doc(\"" + samplesDir + "\\data\\books.xml\") })//schema-element(ITEM)\n" +
                                "return <OUTPUT>{$integer}</OUTPUT>";
            Processor processor = new Processor();

            XQueryCompiler compiler = processor.NewXQueryCompiler();
            compiler.XQueryLanguageVersion = "1.0";
            XQueryExecutable exp = compiler.Compile(query);
            XQueryEvaluator eval = exp.Load();
            Serializer qout = new Serializer();
            eval.Run(qout);
        }

    }

    /// <summary>
    /// Show XPath (Schema aware) example
    /// </summary>

    public class XPathSchemaAware : Example
    {

        public override string testName
        {
            get { return "XPathSchemaAware"; }
        }


        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor(true);


            String inputFileName = new Uri(samplesDir, "data/books.xml").ToString();

            processor.SchemaManager.Compile(new Uri(samplesDir, "data/books.xsd"));

            // add a reader
            XmlReader xmlReader = XmlReader.Create(UriConnection.getReadableUriStream(new Uri(samplesDir, "data/books.xml")));

            DocumentBuilder builder = processor.NewDocumentBuilder();

            builder.SchemaValidationMode = SchemaValidationMode.Strict;
            XdmNode doc = builder.Build(xmlReader);

            XPathCompiler compiler = processor.NewXPathCompiler();
            compiler.ImportSchemaNamespace("");
            XPathExecutable exp = compiler.Compile("if (//ITEM[@CAT='MMP']/QUANTITY instance of element(*,xs:integer)*) then 'true' else 'false'");
            XPathSelector eval = exp.Load();
            eval.ContextItem = doc;
            XdmAtomicValue result = (XdmAtomicValue)eval.EvaluateSingle();
            Console.WriteLine("Result type: " + result.ToString());
        }

    }

    /// <summary>
    /// Show XSLT streaming of document
    /// </summary>

    public class XsltStreamDoc : Example
    {

        public override string testName
        {
            get { return "XsltStreamDoc"; }
        }

        public override void run(Uri samplesDir)
        {
            Processor processor = new Processor(true);

            // Create the stylesheet
            String s = "<xsl:transform version='2.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform' xmlns:saxon='http://saxon.sf.net/'>\n" +
                " <xsl:template name='main'> " +
                " <xsl:value-of select=\"count(saxon:stream(doc('" + new Uri(samplesDir, "data/othello.xml").ToString() + "')//LINE[count(tokenize(.,'/s')) &gt; 0] ))\" />" +
                " </xsl:template></xsl:transform>";

            // Create a transformer for the stylesheet.
            XsltTransformer transformer = processor.NewXsltCompiler().Compile(new StringReader(s)).Load();
            transformer.InitialTemplate = new QName("main");

            // Create a serializer
            Serializer serializer = new Serializer();
            serializer.SetOutputWriter(Console.Out);
            //  serializer.SetOutputProperty(Serializer.INDENT, "yes");

            // Transform the source XML to System.out.
            transformer.Run(serializer);


        }

    }

    /// <summary>
    /// Show validation of an instance document against a schema
    /// </summary>

    public class Validate : Example
    {

        public override string testName
        {
            get { return "EE-Validate"; }
        }

        /// <summary>
        /// Show validation of an instance document against a schema
        /// </summary>

        public override void run(Uri samplesDir)
        {
            // Load a schema

            Processor processor;
            try
            {
                processor = new Processor(true);
            }
            catch (Exception err)
            {
                Console.WriteLine(err);
                Console.WriteLine("Failed to load Saxon-EE (use -HE option to run Saxon-HE tests only)");
                return;
            }
            processor.SetProperty("http://saxon.sf.net/feature/timing", "true");
            processor.SetProperty("http://saxon.sf.net/feature/validation-warnings", "true");
            SchemaManager manager = processor.SchemaManager;
            manager.XsdVersion = "1.1";
            manager.ErrorList = new ArrayList();
            Uri schemaUri = new Uri(samplesDir, "data/books.xsd");

            try
            {
                manager.Compile(schemaUri);
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Console.WriteLine("Schema compilation failed with " + manager.ErrorList.Count + " errors");
                foreach (StaticError error in manager.ErrorList)
                {
                    Console.WriteLine("At line " + error.LineNumber + ": " + error.Message);
                }
                return;
            }


            // Use this to validate an instance document

            SchemaValidator validator = manager.NewSchemaValidator();
            //Uri instanceUri = new Uri(samplesDir, "data/books-invalid.xml");
            //validator.SetSource(instanceUri);
            XmlReader xmlReader = XmlReader.Create(samplesDir + "data/books-invalid.xml");
            validator.SetSource(xmlReader);
            validator.ErrorList = new ArrayList();
            XdmDestination psvi = new XdmDestination();
            validator.SetDestination(psvi);

            try
            {
                validator.Run();
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Console.WriteLine("Instance validation failed with " + validator.ErrorList.Count + " errors");
                foreach (StaticError error in validator.ErrorList)
                {
                    Console.WriteLine("At line " + error.LineNumber + ": " + error.Message);
                }
                return;
            }

            // Run a query on the result to check that it has type annotations

            XQueryCompiler xq = processor.NewXQueryCompiler();
            XQueryEvaluator xv = xq.Compile("data((//PRICE)[1]) instance of xs:decimal").Load();
            xv.ContextItem = psvi.XdmNode;
            Console.WriteLine("Price is decimal? " + xv.EvaluateSingle().ToString());
        }
    }



    public class UriConnection
    {

        // Get a stream for reading from a file:// URI

        public static Stream getReadableUriStream(Uri uri)
        {
            WebRequest request = (WebRequest)WebRequest.Create(uri);
            return request.GetResponse().GetResponseStream();
        }

        // Get a stream for writing to a file:// URI

        public static Stream getWritableUriStream(Uri uri)
        {
            FileWebRequest request = (FileWebRequest)WebRequest.CreateDefault(uri);
            request.Method = "POST";
            return request.GetRequestStream();
        }
    }

    ///
    /// A sample XmlResolver. In the case of a URI ending with ".txt", it returns the
    /// URI itself, wrapped as an XML document. In the case of the URI "empty.xslt", it returns an empty
    /// stylesheet. In all other cases, it returns null, which has the effect of delegating
    /// processing to the standard XmlResolver.
    ///

    public class UserXmlResolver : XmlUrlResolver
    {

        public String Message = null;

        public override object GetEntity(Uri absoluteUri, String role, Type ofObjectToReturn)
        {
            if (Message != null)
            {
                Console.WriteLine(Message + absoluteUri + " (role=" + role + ")");
            }

            if (absoluteUri.ToString().EndsWith(".txt"))
            {
                MemoryStream ms = new MemoryStream();
                StreamWriter tw = new StreamWriter(ms);
                tw.Write("<uri>");
                tw.Write(absoluteUri);
                tw.Write("</uri>");
                tw.Flush();
                return new MemoryStream(ms.GetBuffer(), 0, (int)ms.Length);
            }
            if (absoluteUri.ToString().EndsWith("empty.xslt"))
            {
                String ss = "<transform xmlns='http://www.w3.org/1999/XSL/Transform' version='2.0'/>";
                MemoryStream ms = new MemoryStream();
                StreamWriter tw = new StreamWriter(ms);
                tw.Write(ss);
                tw.Flush();
                return new MemoryStream(ms.GetBuffer(), 0, (int)ms.Length);
            }
            else
            {
                return null;
            }
        }
    }

    public class UserResultDocumentHandler : IResultDocumentHandler
    {

        private Hashtable results;

        public UserResultDocumentHandler(Hashtable table)
        {
            this.results = table;
        }

        public XmlDestination HandleResultDocument(string href, Uri baseUri)
        {
            DomDestination destination = new DomDestination();
            results[href] = destination;
            return destination;
        }

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



