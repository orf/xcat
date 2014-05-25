# I work out *how* to inject payloads into requests
from .requester import RequestMaker
from .injectors import IntegerInjection, SingleQuoteStringInjection, DoubleQuoteStringInjection,\
    AttributeNameInjection, PrefixElementNameInjection, PostfixElementNameInjection
from .. import features
import asyncio
import logbook

logger = logbook.Logger("Detector")


class DetectionException(Exception):
    pass


class Detector(object):
    def __init__(self, url, method, working_data, target_parameter, checker):
        self.checker = checker
        self.requests = RequestMaker(url, method, working_data, target_parameter, checker=self.checker)

    def get_requester(self, injector, features=None):
        requester = self.requests.with_injector(injector)
        if features is not None:
            requester.add_features(features)
        return requester

    @asyncio.coroutine
    def detect_features(self, injector):

        req = self.get_requester(injector)
        x = {
            f.__class__: f
            for f in (yield from features.get_available_features(req))
        }
        return x

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
                    AttributeNameInjection,
                    PrefixElementNameInjection,
                    PostfixElementNameInjection):
            inst = cls(self)
            if (yield from inst.test()):
                injectors.append(inst)

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
