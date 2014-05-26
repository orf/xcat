from collections import namedtuple
import abc
XMLNode = namedtuple("Node", "name attributes comments text child_count children node")


class BaseExecutor(abc.ABC):
    def __init__(self, requester):
        self.requester = requester

    @abc.abstractmethod
    def count(self, expression, count_func):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_char(self, exp):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_string(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def count_nodes(self, node):
        raise NotImplementedError()

    @abc.abstractmethod
    def string_length(self, expression):
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_node(self, node):
        raise NotImplementedError()