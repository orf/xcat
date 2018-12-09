# How it works

There are two concepts that are integral to how xcat works: The **injection** and the **features**.

## Injections

When xcat runs it attempts to find a suitable injection. This is a small snippet we can wrap arbitrary expressions 
inside to evaluate if they are true or false. You can find a full list of supported injections by running 
`xcat injections`. Defining a new injection can be done by adding an entry to the `injectors` 
list inside `injections.py`.

## Features

Once we have the boolean injection primitive xcat can exploit it in a variety of ways. The simplest way 
of extracting text from an XML document is brute-forcing: checking each character one by one against an alphabet. 
However this is really slow, and so xcat attempts to speed this up by detecting what **features** are supported by 
the application. xcat then takes these features and uses the optimal ones to speed up retrieval.

Features are defined in features.py and can be modified by adding a new `Feature` instance with a name and 
an XPath expression to test if it is available.

An example of such a feature is `codepoint-search`, defined like so:

```python
Feature('codepoint-search', [string_to_codepoints("test")[1] == 116])
```

After an injection has been found, but before an attack is commenced, xcat will execute this expression:  
`string-to-codepoints('test')=116`. If it is truthful then it is considered available.

This feature speeds up retrieval by allowing us to binary search the string codepoint 
(see binary_search in algorithms.py) rather than brute forcing it.

There are a variety of other features that can speed up the retrieval, and some may cause slightly different output 
to be retrieved.

For a full rundown of how the features are used then see the algorithms.py file. 

## XPath expressions in Python

XPath expressions are created and composed in pure Python 
[using the xpath-expressions library](https://github.com/orf/xpath-expressions)
