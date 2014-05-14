# I work out *how* to inject payloads into requests
from urllib import parse
from .maker import RequestMaker
from .injectors import IntegerInjection, SingleQuoteStringInjection, DoubleQuoteStringInjection,\
    AttributeInjection, PrefixElementNameInjection, PostfixElementNameInjection
from .. import features
import copy
import asyncio
import logbook

logger = logbook.Logger("Detector")


class DetectionException(Exception):
    pass


class Detector(object):
    def __init__(self, url, method, working_data, target_parameter, checker):
        self.checker = checker
        self.requests = RequestMaker(url, method, working_data, target_parameter, checker=self.checker)

    def get_requester(self, injector):
        return self.requests.with_injector(injector)

    @asyncio.coroutine
    def detect_features(self, injector):
        req = self.get_requester(injector)
        return (yield from features.get_available_features(req))

    @asyncio.coroutine
    def detect_injectors(self):
        """
        Work out how to send a request
        """
        # Run through all our Injection classes and test them
        injectors = []

        for cls in (IntegerInjection,
                    SingleQuoteStringInjection,
                    DoubleQuoteStringInjection,
                    AttributeInjection,
                    PrefixElementNameInjection,
                    PostfixElementNameInjection):
            inst = cls(self)
            if (yield from inst.test()):
                injectors.append(cls)

        return injectors

    def detect_url_stable(self, data, n=5, expected_result=True):
        """
        See if this data is stable (requests return the same code) n times
        """
        logger.info("Testing if URL is stable with {0} requests, expecting {1} response", n, expected_result)

        gathered_results = yield from asyncio.wait([self.requests.send_request(data) for _ in range(n)])
        results = [r.result() == expected_result for r in gathered_results[0]]
        if all(results):
            logger.info("URL is stable")
            return True
        else:
            if any(results):
                logger.info("URL is not stable. Responses: {}", results)
            return False
