from aiohttp import server
import asyncio
import random
import email
import aiohttp
from urllib import parse


class OOBHttpRequestHandler(server.ServerHttpProtocol):
    TEST_RESPONSE = random.randint(1, 150)

    def handle_request(self, message, payload):

        headers = email.message.Message()
        for hdr, val in message.headers:
            print(hdr, val)
            headers.add_header(hdr, val)

        response = aiohttp.Response(
            self.writer, 200, http_version=message.version
        )
        response.add_header('Transfer-Encoding', 'chunked')

        accept_encoding = headers.get('accept-encoding', '').lower()

        if 'deflate' in accept_encoding:
            response.add_header('Content-Encoding', 'deflate')
            response.add_compression_filter('deflate')

        elif 'gzip' in accept_encoding:
            response.add_header('Content-Encoding', 'gzip')
            response.add_compression_filter('gzip')

        response.add_chunking_filter(1025)
        response.add_header('Content-type', 'text/xml')

        response.send_headers()

        if message.path == "/test":
            response.write(bytes("<test>{}</test>".format(self.TEST_RESPONSE), "utf8"))
        else:
            parsed = parse.urlparse(message.path)
            identifier = parsed.path.lstrip("/")
            if not self.server.expecting_identifier(identifier):
                return response.force_close()

            parsed_data = parse.parse_qs(parsed.query)
            self.server.got_data(identifier, parsed_data)

            response.write(bytes("<test>{}</test>".format(identifier), "utf-8"))

        yield from response.write_eof()
        if response.keep_alive():
            self.keep_alive(True)


class OOBHttpServer(object):
    expectations = {}

    def __init__(self, host=None, port=None):
        self.tick = 0
        self.server = None
        self.external_ip, self.port = host, port

    def create_handler(self, *args, **kwargs):
        h = OOBHttpRequestHandler(keep_alive=75)
        h.server = self
        return h

    def expecting_identifier(self, identifier):
        return identifier in self.expectations

    def expect_data(self):
        self.tick += 1
        future = asyncio.Future()
        self.expectations[str(self.tick)] = future
        return str(self.tick), future

    def got_data(self, id, data):
        self.expectations[id].set_result(data)
        del self.expectations[id]

    @asyncio.coroutine
    def start(self, port=None):
        if self.server is not None:
            raise RuntimeError("Server has already been started")

        if port:
            self.port = port

        loop = asyncio.get_event_loop()
        self.server = yield from loop.create_server(
            self.create_handler,
            "0.0.0.0", self.port
        )
        return

    def stop(self):
        if self.server is None:
            raise RuntimeError("Server has not been started!")
        self.server.close()

    @property
    def started(self):
        return self.server is not None

    @property
    def location(self):
        return "http://{}:{}".format(self.external_ip, self.port)

default = OOBHttpServer()