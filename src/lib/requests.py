import asyncio
import aiohttp


class RequestMaker(object):
    def __init__(self, url, true_keyword):
        self.url = url
        self.true_keyword = true_keyword

    def send_request(self, payload):
        response = yield from aiohttp.request("GET", self.url + str(payload))
        body = yield from response.read_and_close()
        return self.true_keyword in body