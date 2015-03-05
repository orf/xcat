import asyncio
import string

from . import BaseExecutor, XMLNode
from ..xpath import count, string_length, substring, translate, normalize_space
from ..features.substring_search import EfficientSubstringSearch


class XPath1Executor(BaseExecutor):
    def count(self, expression, func):
        return (yield from self.requester.binary_search(func(expression)))

    def get_char(self, exp):
        if self.requester.has_feature(EfficientSubstringSearch):
            # Try and use the substring-before method to speed things up
            return self.requester.get_feature(EfficientSubstringSearch).execute(self.requester, exp)
        else:
            # Fallback to dumb searching
            return self.requester.dumb_search(string.digits + string.ascii_letters + string.punctuation + " \r\n\t", exp)

    @asyncio.coroutine
    def get_string(self, expression):
        returner = []
        string_count = yield from self.string_length(expression)

        if (yield from self.is_empty_string(expression)):
            return ""

        def get_string_task(self, expression, i):
            exp = substring(expression, i, 1)
            char = yield from self.get_char(exp)

            if char is None:
                print("Could not get char at index %s: %s" % (i, exp))
                char = "?"

            return char
        
        futures = map(asyncio.Task, (get_string_task(self, expression, i) for i in range(1, string_count + 1) ))
        result = (yield from asyncio.gather(*futures))
        return "".join(result)

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
        return (yield from self.requester.send_payload(
            string_length(translate(normalize_space(expression), " ", "")) == 0
        ))

    @asyncio.coroutine
    def get_attributes(self, node, count):
        attributes = {}
        
        def get_attributes_task(self, attribute):
            attr_name = yield from self.get_string(attribute.name)
            attr_text = yield from self.get_string(attribute)
            return (attr_name, attr_text)

        futures = map(asyncio.Task, (get_attributes_task(self, attribute) for attribute in node.attributes(count)))
        results = (yield from asyncio.gather(*futures))
        attributes = dict(results)
        return attributes

    @asyncio.coroutine
    def get_node_text(self, node, text_count):
        node_text = ""
        for text in node.text(text_count):
            node_text += yield from self.get_string(text)
        return node_text.strip()

    @asyncio.coroutine
    def get_comments(self, node, comment_count):
        comments = []
        for comment in node.comments(comment_count):
            comments.append((yield from self.get_string(comment)))
        return comments

    @asyncio.coroutine
    def retrieve_node(self, node, simple=False):
        # Sub-task that run in parallel to retrieve the information of a node.
        def attributes(self, node):
            attribute_count = yield from self.count_nodes(node.attributes)
            attributes_result = yield from self.get_attributes(node, attribute_count)
            return attributes_result
        
        def child_node_count(self, node):
            child_node_count_result = yield from self.count_nodes(node.children)
            return child_node_count_result

        def text(self, node):
            text_count = yield from self.count_nodes(node.text)
            text_result = yield from self.get_node_text(node, text_count)
            return text_result

        def comments(self, node):
            comment_count = yield from self.count_nodes(node.comments)
            comments_result = yield from self.get_comments(node, comment_count)
            return comments_result

        def node_name(self, node):
            node_name_result = yield from self.get_string(node.name)
            return node_name_result

        @asyncio.coroutine
        def simple_attributes(self, node):
            attribute_count = yield from self.count_nodes(node.attributes)
            attributes_result = {}

            for i in range(attribute_count):
                attributes_result["att%i" % i] = "att%i_placeholder" % i
            
            return attributes_result

        @asyncio.coroutine
        def simple_text(self, node):
            text_count = yield from self.count_nodes(node.text)
            count_not_empty = 0
            
            for text in node.text(text_count):
                if not (yield from self.is_empty_string(text)):
                    count_not_empty += 1
            
            
            if count_not_empty > 0:
                return "%i text node found." % count_not_empty
            else:
                return ""

        @asyncio.coroutine
        def simple_comments(self, node):
            comment_count = yield from self.count_nodes(node.comments)
            comments = ["%i comments found." % comment_count] if comment_count > 0 else []
            return comments
        
        @asyncio.coroutine
        def simple_node_name(self, node):
            node_name_length = yield from self.string_length(node.name)
            
            if node_name_length <= 6:
                node_name_result = yield from self.get_string(node.name)
                return node_name_result
            
            left_part = yield from self.get_string(substring(node.name, 0, 3))
            right_part = yield from self.get_string(substring(node.name, node_name_length - 3, node_name_length))
            remaining = node_name_length - 6
            return "%s ... %i more chracters  ... %s" % (left_part, remaining, right_part)
        
        if simple:
    	    tasks = {
    	        "attributes"       : simple_attributes,
    	        "child_node_count" : child_node_count,
    	        "text"             : simple_text,
    	        "comments"         : simple_comments,
    	        "node_name"        : simple_node_name
    	    }
        else:
    	    tasks = {
    	        "attributes"       : attributes,
    	        "child_node_count" : child_node_count,
    	        "text"             : text,
    	        "comments"         : comments,
    	        "node_name"        : node_name
    	    }
        
        task_list = list(tasks.keys())
		
        futures = map(asyncio.Task, (tasks[task_name](self, node) for task_name in task_list ))
        results = (yield from asyncio.gather(*futures))
        results = dict(zip(task_list, results))
        
        return XMLNode(
            name=results["node_name"],
            attributes=results["attributes"],
            comments=results["comments"],
            text=results["text"],
            child_count=results["child_node_count"],
            node=node,
            children=[]
        )
