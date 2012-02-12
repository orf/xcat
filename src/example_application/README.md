XCat example application
========================

Requires [IronPython](http://ironpython.net/)

Support for XPath 2.0 is not great, so I had to choose between a [Java library](http://saxon.sourceforge.net/) or a [.NET one](http://www.xmlprime.com/xmlprime/download.htm).

This application uses XMLPrime's (rather good) XPath 2.0 library, which can be [downloaded here](http://www.xmlprime.com/xmlprime/download.htm).
Install then copy all the .dll and .xml files (XmlPrime.dll and XmlPrime.ExtensionMethods.dll) to the same directory as input.xml and ironpython_site.py, then run:

	ipy ironpython_site.py
	
to run the sample application. You can use this to try out XCat - the true keyword is "Book found" and an example request string (for xcats --arg flag) is "title=Bible". Run XCat with the flags below to dump the XML file:

	xcat.py --true "Book found" --arg "title=Bible" --method POST http://localhost:80/
	
Have a play with the --regex and --connectback flags
