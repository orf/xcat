from functools import singledispatch


class ExpressionSugar(object):
    def expr(self, symbol, value):
        return Expression("%s%s%s" % (self.value(), symbol, arg_to_representation(value)))

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

    def comment(self):
        return Expression(self.string + "/comment()")

    def text(self):
        return Expression(self.string + "/text()")

    def any_node(self):
        return Expression(self.string + "/node()")

    def add_path(self, path):
        return Expression(self.string + path)

    def count(self):
        return Function("count", self.string)

    def value(self):
        return self.string


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

        self.validate_args(args)
        self.args = args

    def validate_args(self, args):
        if self.args_count != -1 and len(args) != self.args_count:
            raise ValueError("%s requires %s arguments" % (self.string, self.args_count))

        if self.min_args != -1 and len(args) < self.min_args:
            raise ValueError("%s requires at least %s arguments" % (self.string, self.min_args))

        if self.max_args != -1 and len(args) > self.max_args:
            raise ValueError("%s requires at max %s arguments" % (self.string, self.max_args))

    def get_string(self, args):
        str_args = ",".join((arg_to_representation(a) for a in args))
        return "%s(%s)" % (self.string, str_args)

    def __str__(self):
        return self.get_string(self.args)

    def __call__(self, *args):
        call_args = self.args + args
        self.validate_args(call_args)
        return self.get_string(call_args)

    def __repr__(self):
        return "<Function: %s %s>" % (self.string, self.args)


A = Attribute
E = Expression
F = Function


@singledispatch
def arg_to_representation(other):
        return str(other)

@arg_to_representation.register(str)
def _(other):
    return "'%s'" % other

@arg_to_representation.register(Expression)
def _(other):
    return "(%s)" % other
