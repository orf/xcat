import asyncio
import itertools

from .xpath2 import XPath2Executor
from . import XMLNode
from ..features.oob_http import OOBDocFeature
from ..xpath import count, string


class DocFunctionExecutor(XPath2Executor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature = self.requester.get_feature(OOBDocFeature)

    @asyncio.coroutine
    def get_string(self, expression):
        result = yield from self.feature.execute(self.requester, expression)

        if result is None:
            return (yield from super().get_string(expression))

        return result[0]

    @asyncio.coroutine
    def get_nodes(self, nodes):
        return (yield from self.feature.execute_many(self.requester, nodes))

    @asyncio.coroutine
    def retrieve_node(self, node):
        # get the node name, attribute count, child node count, text count and comments count
        # in one fell swoop.
        result = yield from self.feature.execute_many(self.requester, (
            node.name,
            string(count(node.attributes)),
            string(count(node.children)),
            string(count(node.text)),
            string(count(node.comments))
        ))

        if result is None:
            return (yield from super().retrieve_node(node))

        node_name = result[0]
        attribute_count, child_count, text_count, comment_count = map(int, result[1:])
        attribute_queries = itertools.chain(
            *((attr.name, attr) for attr in node.attributes(int(attribute_count)))
        )
        attributes = yield from self.feature.execute_many(self.requester, attribute_queries)

        if attributes is None:
            attributes = yield from super().get_attributes(node, attribute_count)
        else:
            # Combine the lists into key-value pairs
            attributes = dict(itertools.zip_longest(
                attributes[0:None:2], attributes[1:None:2]
            ))

        node_text = yield from self.feature.execute_many(self.requester, node.text(text_count))
        if node_text is None:
            node_text = yield from super().get_node_text(node, text_count)
        else:
            node_text = "".join(node_text).strip()

        comments = yield from self.feature.execute_many(self.requester, node.comments(comment_count))

        if comments is None:
            comments = yield from super().get_comments(node, comment_count)

        return XMLNode(
            name=node_name,
            attributes=attributes,
            comments=comments,
            text=node_text,
            child_count=child_count,
            node=node,
            children=[]
        )