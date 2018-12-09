# Introduction

xcat is an advanced tool for exploiting XPath injection vulnerabilities, featuring a comprehensive 
set of features to read the entire file being queried as well as other files on the filesystem, 
environment variables and directories.

## Quickstart

The easiest way to get started is to install the tool via pip:

`pip install xcat`

You can then use the `xcat` command to launch attacks. 
See [commands](commands.md) for a full reference.

There [is also a demo application you can run to test xcat](https://github.com/orf/xcat_app)

## Demo

This demo shows xcat retrieving the full current XML file being queried, including data that should
be private (passwords). It uses the `--fast` option to speed up retrieval. [See the command reference](commands.md) 
for a full rundown of what XCat can do and how to use it.

<script id="asciicast-216031" src="https://asciinema.org/a/216031.js" async></script>

## XPath functions reference

There is an amazing reference with all the available XPath functions here: [https://maxtoroq.github.io/xpath-ref/]()
