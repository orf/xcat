from .xpath2 import XPath2Executor
import asyncio
from ..features.doc import DocFeature


class DocFunctionExecutor(XPath2Executor):

    @asyncio.coroutine
    def get_string(self, expression):
        feature = self.requester.get_feature(DocFeature)
        result = yield from feature.execute(self.requester, expression)

        if result is None:
            return (yield from super().get_string(expression))

        return result["d"][0]


    @asyncio.coroutine
    def retrieve_node(self, node):
        # ToDo: Make this use the doc function
        pass