using System;
using System.IO;
using System.Collections;
using System.Xml;
using System.Collections.Generic;
using System.Text;
using Saxon.Api;

namespace TestRunner
{
    /// <summary>
    /// Code to compare actual results of a test (outfile) with reference results (reffile).
    /// The parameter comparator is the name of a comparison method: xml, html, xml-frag, xhtml, inspect.
    /// The return value is "OK" if the files compare equal. Any string starting with "#" indicates the files are
    /// considered equal but with a comment (e.g. that they are equal after removing whitespace). Any other string indicates
    /// not equal, with an explanation of why.
    /// </summary>

    
    class FileComparer
    {
        private Processor processor;
        private String comparerDir = "e:/tests/comparers/";
        bool debug = false;

        public FileComparer(Processor processor, String testSuiteDir)
        {
            this.processor = processor;
            //this.testSuiteDir = testSuiteDir;
        }

        public String compare(String outfile, String reffile, String comparator)
        {
            if (comparator == "Ignore")
            {
                return "OK";
            }
            if (reffile == null || !File.Exists(reffile))
            {
                Console.WriteLine("*** No reference results available");
                return "No reference results available";
            }

            // try direct comparison first

            String refResult = null;
            String actResult = null;

            try
            {
                // This is decoding bytes assuming the platform default encoding
                StreamReader reader1;
                try
                {
                    reader1 = new StreamReader(outfile);
                }
                catch (Exception err)
                {
                    Console.WriteLine("Failed to read output file " + outfile + ": " + err);
                    return "Failed to read output file " + outfile + ": " + err;
                }
                StreamReader reader2;
                try
                {
                    reader2 = new StreamReader(reffile);
                }
                catch (Exception err)
                {
                    Console.WriteLine("Failed to read reference file " + reffile + ": " + err);
                    return "Failed to read reference file " + reffile + ": " + err;
                }

                char[] contents1 = new char[65536];
                char[] contents2 = new char[65536];
                int size1 = reader1.Read(contents1, 0, 65536);
                int size2 = reader2.Read(contents2, 0, 65536);
                reader1.Close();
                reader2.Close();

                int offset1 = 0;
                int offset2 = 0;
                if (contents1[0] == '\u00ef' && contents1[1] == '\u00bb' && contents1[2] == '\u00bf')
                {
                    offset1 += 3;
                }
                if (contents2[0] == '\u00ef' && contents2[1] == '\u00bb' && contents2[2] == '\u00bf')
                {
                    offset2 += 3;
                }
                actResult = (size1 == -1 ? "" : new String(contents1, offset1, size1 - offset1));
                refResult = (size2 == -1 ? "" : new String(contents2, offset2, size2 - offset2));

                actResult = actResult.Replace("\r\n", "\n");
                refResult = refResult.Replace("\r\n", "\n");
                if (actResult.Equals(refResult))
                {
                    return "OK";
                }
                if (size1 == 0)
                {
                    Console.WriteLine("** ACTUAL RESULTS EMPTY; REFERENCE RESULTS LENGTH " + size2);
                    return "** ACTUAL RESULTS EMPTY; REFERENCE RESULTS LENGTH " + size2;
                }
                if (size2 == 0)
                {
                    Console.WriteLine("** REFERENCED RESULTS EMPTY; ACTUAL RESULTS LENGTH " + size2);
                    return "** REFERENCED RESULTS EMPTY; ACTUAL RESULTS LENGTH " + size2;
                }

            }
            catch (Exception e)
            {
                Console.Write(e.StackTrace);
                return "Exception: " + e.Message;
            }

            // HTML: can't do logical comparison

            if (comparator.Equals("html-output"))
            {

                Console.WriteLine("*** Compare HTML outputs by hand");
                return "Compare HTML outputs by hand";

            }
            else if (comparator.Equals("xhtml-output"))
            {
                refResult = canonizeXhtml(processor, refResult);
                actResult = canonizeXhtml(processor, actResult);
                return (actResult.Equals(refResult)) ? "OK" : "XHTML canonical results differ";

            }
            else if (comparator.Equals("xml-frag") || comparator.Equals("Text") || comparator.Equals("Fragment"))
            {
                try
                {
                    return compareFragments(actResult, refResult);
                }
                catch (Exception err2)
                {
                    Console.WriteLine("Failed to compare results for: " + outfile);
                    Console.Write(err2.StackTrace);
                    return "Failure while comparing fragments: " + err2.Message;
                }
            }
            else
            {
                // convert both files to Canonical XML and compare them again
                return compareXML(outfile, reffile);

            }
        }

        XsltExecutable xhtmlCanonizer;

        private String canonizeXhtml(Processor p, String input)
        {
            try
            {
                XsltExecutable canonizer = getXhtmlCanonizer(p);
                XsltTransformer t = canonizer.Load();
                StringWriter sw = new StringWriter();
                Serializer r = new Serializer();
                r.SetOutputWriter(sw);
                t.InitialContextNode = p.NewDocumentBuilder().Build(
                    new FileStream(input, FileMode.Open));
                t.Run(r);
                return sw.ToString();
            }
            catch (Exception err)
            {
                Console.WriteLine("*** Failed to compile or run XHTML canonicalizer stylesheet: " + err.ToString());
            }
            return "";
        }

        private XsltExecutable getXhtmlCanonizer(Processor p)
        {
            if (xhtmlCanonizer == null)
            {
                xhtmlCanonizer = p.NewXsltCompiler().Compile(
                    new FileStream(comparerDir + "/canonizeXhtml.xsl", FileMode.Open));
            }
            return xhtmlCanonizer;
        }

        /// <summary>
        /// Compare XML fragments
        /// </summary>
        /// <param name="actual">Actual results (the results, not the filename)</param>
        /// <param name="gold">Reference results (the results, not the filename)</param>
        /// <returns>"OK" if equivalent</returns>

        private String compareFragments(String actual, String gold)
        {

            String a = "<d>" + expandSpecialChars(actual) + "</d>";
            String g = "<d>" + expandSpecialChars(gold) + "</d>";
            XdmNode doc1;
            try
            {
                doc1 = processor.NewDocumentBuilder().Build(
                    new XmlTextReader(new StringReader(a)));
            }
            catch (Exception e)
            {
                //Console.WriteLine(e.StackTrace);
                Console.WriteLine("*** Error parsing actual results " + e.Message);
                Console.WriteLine(a);
                return "*** Error parsing actual results " + e.Message;
            }
            XdmNode doc2;
            try
            {
                doc2 = processor.NewDocumentBuilder().Build(
                    new XmlTextReader(new StringReader(g)));
            }
            catch (Exception e)
            {
                //Console.WriteLine(e.StackTrace);
                Console.WriteLine("*** Error parsing gold results " + e.Message);
                Console.WriteLine(g);
                return "*** Error parsing gold results " + e.Message;
            }
            try
            {
                return compareDocs(doc1, doc2);
            }
            catch (Exception e)
            {
                //Console.WriteLine(e.StackTrace);
                Console.WriteLine("*** Error comparing results " + e.Message);
                return "*** Error comparing results " + e.Message;
            }
        }

        private String expandSpecialChars(String s)
        {
            StringBuilder sb = new StringBuilder();
            int start = 0;
            if (s.StartsWith("<?xml"))
            {
                start = s.IndexOf("?>") + 2;
            }
            for (int i = start; i < s.Length; i++)
            {
                char c = s[i];
                if (c < 127)
                {
                    sb.Append(c);
                }
                else if (c >= 55296 && c <= 56319)
                {
                    // we'll trust the data to be sound
                    int charval = ((c - 55296) * 1024) + ((int)s[i + 1] - 56320) + 65536;
                    sb.Append("&#" + charval + ";");
                    i++;
                }
                else
                {
                    sb.Append("&#" + ((int)c) + ";");
                }
            }
            return sb.ToString();
        }

        private static String truncate(String s)
        {
            if (s.Length > 200) return s.Substring(0, 200);
            return s;
        }

        private static void findDiff(String s1, String s2)
        {
            int i = 0;
            while (true)
            {
                if (s1[i] != s2[i])
                {
                    int j = (i < 50 ? 0 : i - 50);
                    int k = (i + 50 > s1.Length || i + 50 > s2.Length ? i + 1 : i + 50);
                    Console.WriteLine("Different at char " + i + "\n+" + s1.Substring(j, k) +
                                       "\n+" + s2.Substring(j, k));
                    break;
                }
                if (i >= s1.Length) break;
                if (i >= s2.Length) break;
                i++;
            }
        }



        private XsltExecutable xmlComparer = null;

        /// <summary>
        /// Compare two XML files
        /// </summary>
        /// <param name="actual">The URI of the first file</param>
        /// <param name="gold">The URI of the second file</param>
        /// <returns></returns>

        private String compareXML(String actual, String gold)
        {
            try
            {
                if (xmlComparer == null)
                {
                    xmlComparer = processor.NewXsltCompiler().Compile(new Uri(comparerDir + "/compare.xsl"));
                }
                XdmNode doc1 = processor.NewDocumentBuilder().Build(new Uri(actual));
                XdmNode doc2 = processor.NewDocumentBuilder().Build(new Uri(gold));
                return compareDocs(doc1, doc2);
            }
            catch (Exception e)
            {
                Console.WriteLine("***" + e.Message);
                return "XML comparison failure: " + e.Message;
            }
        }

        private String compareDocs(XdmNode doc1, XdmNode doc2) {
            try {
                XsltTransformer t = xmlComparer.Load();
                t.InitialTemplate = new QName("", "compare");
                t.SetParameter(new QName("", "actual"), doc1);
                t.SetParameter(new QName("", "gold"), doc2);
                t.SetParameter(new QName("", "debug"), new XdmAtomicValue(debug));

                StringWriter sw = new StringWriter();
                Serializer sr = new Serializer();
                sr.SetOutputWriter(sw);

                t.Run(sr);
                String result = sw.ToString();
                if (result.StartsWith("true"))
                {
                    return "OK";
                }
                else
                {
                    return "XML comparison - not equal";
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("***" + e.Message);
                return "XML comparison failure: " + e.Message;
            }
        }

    }
}
