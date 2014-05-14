import asyncio
import string
from . import BaseExecutor, XMLNode
from ..xpath.expression import count, string_length, substring, translate, normalize_space
from ..features.substring_search import EfficientSubstringSearch


class XPath1Executor(BaseExecutor):
    def count(self, expression, func):
        return (yield from self.requester.binary_search(func(expression)))

    @asyncio.coroutine
    def get_string(self, expression):
        returner = []
        string_count = yield from self.string_length(expression)

        if (yield from self.is_empty_string(expression)):
            return ""

        for i in range(1, string_count + 1):
            exp = substring(expression, i, 1)
            if self.requester.has_feature(EfficientSubstringSearch):
                # Try and use the substring-before method to speed things up
                char = yield from EfficientSubstringSearch.execute(self.requester, exp)
            else:
                # Fallback to dumb searching
                char = yield from self.requester.dumb_search(string.ascii_letters + string.digits + " ", exp)
            if char is None:
                print("Could not get char at index %s: %s" % (i, substring(expression, i, 1)))
                char = "?"
            returner.append(char)
        return "".join(returner)

    @asyncio.coroutine
    def count_nodes(self, expression):
        return (yield from self.count(expression, func=count))

    @asyncio.coroutine
    def string_length(self, expression):
        if (yield from self.is_empty_string(expression)):
            return 0
        return (yield from self.count(expression, func=string_length))

    @asyncio.coroutine
    def is_empty_string(self, expression):
        return (yield from self.requester.send_request(
            string_length(translate(normalize_space(expression), " ", "")) == 0
        ))

    @asyncio.coroutine
    def retrieve_node(self, node):
        node_name = yield from self.get_string(node.name)

        attribute_count = yield from self.count_nodes(node.attributes)
        attributes = {}
        for attribute in node.attributes(attribute_count):
            attr_name = yield from self.get_string(attribute.name)
            attr_text = yield from self.get_string(attribute)
            attributes[attr_name] = attr_text

        text_count = yield from self.count_nodes(node.text)
        node_text = ""
        for text in node.text(text_count):
            node_text += yield from self.get_string(text)

        comment_count = yield from self.count_nodes(node.comments)
        comments = []
        for comment in node.comments(comment_count):
            comments.append((yield from self.get_string(comment)))

        child_node_count = yield from self.count_nodes(node.children)

        return XMLNode(
            name=node_name,
            attributes=attributes,
            comments=comments,
            text=node_text,
            child_count=child_node_count,
            node=node,
            children=[]
        )