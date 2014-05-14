from collections import namedtuple

XMLNode = namedtuple("Node", "name attributes comments text child_count children node")


class BaseExecutor(object):
    def __init__(self, requester):
        self.requester = requester

    def count_nodes(self, expression):
        raise NotImplementedError()

    def count_string(self, expression):
        raise NotImplementedError()

    def get_xml_from_node(self, node):
        raise NotImplementedError()