# I work out *how* to inject payloads into requests
import asyncio
import copy
import logbook

from .injectors import IntegerInjection, StringInjection, AttributeNameInjection, \
    FunctionCallInjection, ElementNameInjection
from .. import features


logger = logbook.Logger("Detector")


class DetectionException(Exception):
    pass


class Detector(object):
    def __init__(self, checker, requestmaker):
        self.checker = checker
        self.requests = requestmaker

    def change_parameter(self, target_parameter):
        """
        :param target_parameter: A parameter name that the returned detector targets
        :return: A Detector that targets the given URI parameter
        """
        d = Detector(self.checker, copy.deepcopy(self.requests))
        d.requests.set_target_parameter(target_parameter)
        return d

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
                    StringInjection,
                    AttributeNameInjection,
                    ElementNameInjection,
                    FunctionCallInjection):
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
