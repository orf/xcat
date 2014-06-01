from functools import singledispatch


class ExpressionSugar(object):
    def expr(self, symbol, value):
        return Expression("%s%s%s" % (self.value(), symbol, arg_to_representation(value)))

    def __getitem__(self, item):
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

    def __div__(self, other):
        return self.expr("/", other)

    def __and__(self, other):
        return self.expr(" and ", other)

    def __or__(self, other):
        return self.expr(" or ", other)

    def value(self):
        raise NotImplementedError()

    def __unicode__(self):
        return "%s" % self.value()

    def __str__(self):
        return "%s" % self.value()


class Expression(ExpressionSugar):
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
        return count(self)

    @property
    def name(self):
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


class Node(Expression):
    pass


class IterableExpression(Expression):
    def __call__(self, count):
        for i in range(1, count+1):
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
    return "'%s'" % other

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

position = Function("position")
count = Function("count")

translate = Function("translate", args_count=3)
string = Function("string")
concat = Function("concat")
starts_with = Function("starts-with")
contains = Function("contains")
substring = Function("substring", args_count=3)
substring_before = Function("substring-before", args_count=2)
substring_after = Function("substring-after", args_count=2)
string_length = Function("string-length")
normalize_space = Function("normalize-space")
_not = Function("not")
_true = Function("true")
_false = Function("false")
_sum = Function("sum")
name = Function("name", args_count=1)

# XPath 2.0 functions
lower_case = Function("lower-case")
string_to_codepoints = Function("string-to-codepoints", args_count=1)
normalize_unicode = Function("normalize-unicode", args_count=1)
document_uri = Function("document-uri", args_count=1)
doc = Function("doc", args_count=1)
encode_for_uri = Function("encode-for-uri", args_count=1)