from .feature import BaseFeature
import asyncio
from ..xpath.functions import lower_case


class XPathVersionFeature(BaseFeature):
    def __init__(self):
        super().__init__("XPath Version")

    @asyncio.coroutine
    def Execute(self, requester, future):
        result = requester.send_request(
            payload=lower_case('A') == 'a'
        )
        if result:
            future.set_result(2)
        else:
            future.set_result(1)