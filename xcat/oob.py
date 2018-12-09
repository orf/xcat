import asyncio
import random
from typing import Tuple
from urllib import parse

from aiohttp import web

ENTITY_INJECTION_TEMPLATE = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                            '<!DOCTYPE stuff [<!ELEMENT data ANY> <!ENTITY goodies {0}>]> <data>&goodies;</data>'

router = web.RouteTableDef()


@router.get('/test/data')
async def test_handler(request: web.Request):
    return web.Response(body=f"<data>{request.app['test_response_value']}</data>", content_type='text/xml')


@router.get('/test/entity')
async def test_entity_handler(request: web.Request):
    return web.Response(body=ENTITY_INJECTION_TEMPLATE.format(f'"{request.app["test_response_value"]}"'),
                        content_type='text/xml')


@router.get('/entity/{id}')
async def entity_handler(request: web.Request):
    file_id = request.match_info["id"]
    if file_id not in request.app['expectations']:
        return web.Response(status=404)

    value = request.app['entity_values'][file_id]
    return web.Response(body=ENTITY_INJECTION_TEMPLATE.format(value), content_type='text/xml')


@router.get('/data/{id}')
async def data_handler(request: web.Request):
    expect_id = request.match_info['id']
    if expect_id not in request.app['expectations']:
        return web.Response(status=404)

    data = parse.unquote(request.rel_url.query_string[2:])
    future: asyncio.Future = request.app['expectations'][expect_id]
    if future.done():
        return web.Response(body=f'Error: {expect_id} used twice', status=400)
    future.set_result(data)
    return web.Response(body=f"<data>{request.app['test_response_value']}</data>", content_type='text/xml')


def create_app():
    app = web.Application(client_max_size=1024 * 1024 * 1024)
    app.router.add_routes(router)
    app['test_response_value'] = random.randint(1, 1000000)
    app['expectations'] = {}
    app['entity_values'] = {}
    return app


def expect_data(app: web.Application) -> Tuple[str, asyncio.Future]:
    expectations = app['expectations']
    identifier = str(len(expectations))
    future = asyncio.Future()
    expectations[identifier] = future
    return identifier, future


def expect_entity_injection(app: web.Application, entity_value):
    identifier, future = expect_data(app)
    app['entity_values'][identifier] = entity_value
    return identifier, future
