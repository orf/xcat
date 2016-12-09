import asyncio
from typing import List, Callable, Dict
from collections import defaultdict, Counter
import aiohttp
from urllib.parse import quote

from xcat.oob import OOBHttpServer


def process_parameters(params: List[str]) -> Dict[str, str]:
    returner = {}

    for param in params:
        key, value = param.split('=')
        returner[key] = value

    return returner


class Requester:
    def __init__(self, url: str, target_parameter: str, parameters: List[str],
                 matcher: Callable[[aiohttp.Response, str], bool],
                 session: aiohttp.ClientSession, concurrency=10, method="get",
                 injector: Callable[[str, str], str]=None,
                 external_ip=None, external_port=0,
                 fast=False):
        self.url = url
        self.parameters = process_parameters(parameters)

        if target_parameter not in self.parameters:
            present_keys = ", ".join(self.parameters.keys())
            raise RuntimeError(f'Target parameter {target_parameter} not present, available choices: {present_keys}')

        self.target_parameter = target_parameter
        self.matcher = matcher
        self.semaphore = asyncio.BoundedSemaphore(value=concurrency)
        self.session = session
        self.method = method
        self.injector = injector

        self.counters = defaultdict(Counter)
        self.features = defaultdict(bool)
        self.fast = fast
        self.request_count = 0

        self.external_ip = external_ip
        self.external_port = external_port
        self._oob_server_lock = asyncio.Lock()
        self._oob_server = None

    async def get_oob_server(self):
        if self.external_ip is None:
            return None

        async with self._oob_server_lock:
            if self._oob_server:
                return self._oob_server

            server = OOBHttpServer(self.external_ip, self.external_port)
            await server.start()
            self._oob_server = server

            return server

    async def stop_oob_server(self):
        await self._oob_server.stop()

    @property
    def target_parameter_value(self):
        return self.parameters[self.target_parameter]

    def payload_to_parameters(self, payload: str):
        params = self.parameters.copy()

        if self.injector is not None:
            params[self.target_parameter] = self.injector(self.target_parameter_value, payload)
        else:
            params[self.target_parameter] = str(payload)

        for param in params:
            params[param] = quote(params[param], safe='')

        return params

    async def check(self, payload) -> bool:
        async with self.semaphore:
            params = self.payload_to_parameters(payload)
            response = await self.session.request(self.method, self.url, params=params)
            body = await response.text()
            self.request_count += 1
            return self.matcher(response, body)
