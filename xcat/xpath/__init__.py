from functools import singledispatch


class Expression:
    __slots__ = ('string',)

    def __init__(self, string=""):
        self.string = string

    def __repr__(self):
        return "<Expression: %s>" % self.string

    @property
    def text(self):
        return IterableExpression(self.string + "/text()")

    @property
    def any_node(self):
        return Expression(self.string + "/node()")

    def add_path(self, path):
        return Expression(self.string + path)

    @property
    def count(self):
        from .xpath_1 import count
        return count(self)

    @property
    def name(self):
        from .xpath_1 import name
        return name(self)

    def value(self):
        return self.string

    @property
    def attributes(self):
        return AttributesExpression("%s/@*" % self.string)

    @property
    def comments(self):
        return CommentsExpression(self.string + "/comment()")

    @property
    def children(self):
        return IterableExpression("%s/*" % self.string)

    def expr(self, symbol, value):
        return Expression("%s%s%s" % (self.value(), symbol, arg_to_representation(value)))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [
                self[idx]
                for idx in range(item.start or 1, item.stop, item.step or 1)
            ]

        return Expression("%s[%s]" % (self.value(), item))

    def __eq__(self, other):
        return self.expr("=", other)

    def __ne__(self, other):
        return self.expr("!=", other)

    def __lt__(self, other):
        return self.expr("<", other)

    def __gt__(self, other):
        return self.expr(">", other)

    def __le__(self, other):
        return self.expr("<=", other)

    def __ge__(self, other):
        return self.expr(">=", other)

    def __add__(self, other):
        return self.expr("+", other)

    def __sub__(self, other):
        return self.expr("-", other)

    def __mul__(self, other):
        return self.expr("*", other)

    def __truediv__(self, other):
        return Expression(f'{self.string}/{other}')

    def __and__(self, other):
        return self.expr(" and ", other)

    def __or__(self, other):
        return self.expr(" or ", other)

    def __unicode__(self):
        return "%s" % self.value()

    def __str__(self):
        return "%s" % self.value()


class Node(Expression):
    pass


class IterableExpression(Expression):
    def __call__(self, count):
        for i in range(1, count + 1):
            yield self[i]


class CommentsExpression(IterableExpression):
    pass


class AttributesExpression(IterableExpression):
    pass


class Attribute(Expression):
    def __repr__(self):
        return "<Attribute: %s>" % self.string

    def value(self):
        return "@%s" % self.string


class Function(Expression):
    __slots__ = ('string', 'min_args', 'max_args', 'args_count', 'args')

    def __init__(self, name, *args, args_count=-1, min_args=-1, max_args=-1):
        super().__init__(name)
        self.min_args = min_args
        self.max_args = max_args
        self.args_count = args_count

        self.args = args

    def validate_args(self, args):
        if self.args_count != -1 and len(args) != self.args_count:
            raise ValueError("%s requires %s arguments. Args: %s" % (self.string, self.args_count, args))

        if self.min_args != -1 and len(args) < self.min_args:
            raise ValueError("%s requires at least %s arguments. Args: %s" % (self.string, self.min_args, args))

        if self.max_args != -1 and len(args) > self.max_args:
            raise ValueError("%s requires at max %s arguments. Args: %s" % (self.string, self.max_args, args))

    def get_string(self, args):
        str_args = ",".join((arg_to_representation(a) for a in args))
        return "%s(%s)" % (self.string, str_args)

    def __str__(self):
        self.validate_args(self.args)
        return self.get_string(self.args)

    def __call__(self, *args):
        call_args = self.args + args
        self.validate_args(call_args)
        return Expression(self.get_string(call_args))

    def __repr__(self):
        return "<Function: %s %s>" % (self.string, self.args)


class Literal(Expression):
    pass


@singledispatch
def arg_to_representation(other):
    return str(other)


@arg_to_representation.register(str)
def _(other):
    if "'" not in str(other):
        return "'%s'" % other

    if '"' not in str(other):
        return '"%s"' % other

    safe_concat = ",".join(arg_to_representation(c) for c in str(other))
    safe_concat = safe_concat.replace('","', '')
    safe_concat = safe_concat.replace("','", '')
    return "concat(" + safe_concat + ")"


@arg_to_representation.register(Expression)
def _(other):
    return "(%s)" % other


@arg_to_representation.register(Literal)
def _(other):
    return str(other)


A = Attribute
E = Expression
L = Literal
F = Function
N = Node

ROOT_NODE = E('/*[1]')
