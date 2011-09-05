XCat example application
========================

Requires [IronPython](http://ironpython.net/)

Support for XPath 2.0 is not great, so I had to choose between a [Java library](http://saxon.sourceforge.net/) or a [.NET one](http://www.xqsharp.com/xqsharp/index.htm).

This application uses XQSharp's (rather good) XPath 2.0 library, which can be [downloaded here](http://www.xqsharp.com/xqsharp/download.htm). Extract all the .dll and .xml files to the same directory as input.xml and ironpython_site.py, then run:

	ipy ironpython_site.py
	
to run the sample application. You can use this to try out XCat - the true keyword is "Book found" and an example request string (for xcats --arg flag) is "title=Bible". Run XCat with the flags below to dump the XML file:

	xcat.py --true "Book found" --arg "title=Bible" --method POST http://localhost:80/
	
Have a play with the --regex and --connectback flags
