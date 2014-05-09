from functools import singledispatch
from .expression import Expression


class BaseNode(object):
    leaf = False

    def __init__(self, exp=""):
        if isinstance(exp, str):
            exp = Expression(exp)

        self.exp = exp

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.exp)

    def select_index(self, i):
        return IndexNode("%s[%i]" % (self.exp, i))

    def select_attribute_exists(self, name):
        return IndexNode("%s[@%s]" % (self.exp, name))

    def select_expression(self, expression):
        return IndexNode("%s[%s]" % (self.exp, expression))

    @singledispatch
    def __getitem__(self, item):
        raise NotImplementedError("__getitem__ not implemented for type %s" % type(item))

    @__getitem__.register(int)
    def _(self, item):
        return self.select_index(item)

    @__getitem__.register(Expression)
    def _(self, expression):
        return self.select_expression(expression)

    @__getitem__.register(str)
    def _(self, item):
        return self.select_attribute_exists(item)

    def __str__(self):
        return str(self.exp)


class TextNode(BaseNode):
    leaf = True


class CommentNode(BaseNode):
    leaf = True
    pass


class Node(BaseNode):
    def comment(self):
        return CommentNode(self.exp.comment())

    def text(self):
        return TextNode(self.exp.text())

    def any_node(self):
        return Node(self.exp.any_node())

    def add_path(self, path):
        return Node(self.exp.add_path(path))

    def __index__(self):
        pass


class IndexNode(Node):
    pass