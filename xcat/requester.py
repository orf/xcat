import asyncio
from typing import List, Callable, Dict
from collections import defaultdict, Counter
import aiohttp
from urllib.parse import quote


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
                 injector: Callable[[str, str], str]=None):
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

            return self.matcher(response, body)
