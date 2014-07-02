using System;
using System.Collections;
using System.Text;
using Saxon.Api;
using System.Xml;

namespace SampleExtensions
{

    /// <summary>
    /// This class contains some example methods that can be invoked from XSLT as
    /// extension functions or from XQuery as external functions. For examples of calls
    /// on these functions, from both XSLT and XQuery, see the Examples.cs program.
    /// </summary>

    public class SampleExtensions
    {

        /// <summary>
        /// Add two numbers
        /// </summary>

        public static double add(double one, double two)
        {
            return one + two;
        }

        /// <summary>
        /// Get the average of an array of numbers
        /// </summary>

        public static double average(double[] numbers)
        {
            double total = 0.0e0;
            foreach (double d in numbers)
            {
                total += d;
            }
            return total / numbers.Length;
        }

        /// <summary>
        /// Get the current host language from the Saxon context
        /// </summary>

        public static string hostLanguage(net.sf.saxon.expr.XPathContext context)
        {
            int lang = context.getController().getExecutable().getHostLanguage();
            if (lang == net.sf.saxon.Configuration.XQUERY)
            {
                return "XQuery";
            }
            else if (lang == net.sf.saxon.Configuration.XSLT)
            {
                return "XSLT";
            }
            else if (lang == net.sf.saxon.Configuration.XPATH)
            {
                return "XPath";
            }
            else
            {
                return "unknown";
            }
        }

        /// <summary>
        /// Get the local name of the first child of the node supplied as an argument
        /// (Shows that an extension function can accept an XmlNode: this only works if
        /// the input document is a wrapper around an XmlDocument)
        /// </summary>

        public static string nameOfFirstChild(XmlNode current)
        {
            return current.FirstChild.LocalName;
        }

        /// <summary>
        /// Get the first child of the node supplied as an argument
        /// (Shows that an extension function can return an XmlNode)
        /// </summary>

        public static XmlNode FirstChild(XmlNode current)
        {
            return current.FirstChild;
        }

        /// <summary>
        /// Accept a node and an atomic value and return the sequence containing the string
        /// value of the node followed by the value.
        /// </summary>

        public static XdmValue combine(XdmNode node, XdmAtomicValue value)
        {
            ArrayList list = new ArrayList();
            list.Add(new XdmAtomicValue(node.StringValue));
            list.Add(value);
            return new XdmValue(list);
        }

        //public static string shorten(string instr) {
        //    throw new NullReferenceException("thrown deliberately");
        //    return String.Empty;
        //}

    }
}
