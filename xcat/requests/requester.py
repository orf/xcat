# I make HTTP requests

from urllib import parse
import copy
import asyncio

import aiohttp
import logging
from ..xpath import Expression

logger = logging.getLogger("xcat.requests")


class RequestMaker(object):
    def __init__(self, url, method, target_parameter, checker, limit_request=20, features=None, injector=None,
                 cookies=None):
        self.method = method
        self.original_url = url
        self.cookies = cookies

        parsed = parse.urlparse(url)

        self.url = "{scheme}://{netloc}{path}".format(scheme=parsed.scheme, netloc=parsed.netloc, path=parsed.path)

        qs = parse.urlparse(url).query
        self.working_data = parse.parse_qs(qs, keep_blank_values=True)

        if target_parameter:
            if target_parameter not in self.working_data:
                logger.error("Parameter %s cannot be found in the given data", target_parameter)
                raise RuntimeError("Unknown parameter {0}".format(target_parameter))

            self.set_target_parameter(target_parameter)

        self.features = features or {}
        self.requests_sent = 0
        self.checker = checker
        self.injector = injector
        self.limit_request = limit_request
        self.semaphore = asyncio.Semaphore(limit_request)

        self.request_count = 0

    def set_target_parameter(self, target_parameter):
        self.param_value = self.working_data[target_parameter][0]
        self.target_parameter = target_parameter

    def get_url_parameters(self):
        """
        :return: A list of URL parameter names that form part of the query being exploited
        """
        return self.working_data.keys()

    def add_features(self, features):
        self.features.update(features)

    def has_feature(self, feature):
        return feature in self.features

    def get_feature(self, cls):
        return self.features[cls]

    def with_injector(self, injector):
        return RequestMaker(self.original_url, self.method, self.target_parameter, self.checker,
                            self.limit_request, self.features, injector, self.cookies)

    def get_query_data(self, new_target_data):
        new_dict = copy.deepcopy(self.working_data)
        new_dict[self.target_parameter] = [new_target_data]
        return parse.urlencode(new_dict, doseq=True)

    def send_raw_request(self, data):
        # Limit the number of concurrent request
        with (yield from self.semaphore):
            logger.debug("Sending request with data %s", data)
            self.request_count += 1

            if isinstance(data, dict):
                data = parse.urlencode(data, doseq=True)
            elif isinstance(data, Expression):
                # Make data
                data = str(data)

            if self.method == "GET":
                url = self.url + "?" + data
                data = None
            else:
                url = self.url

            headers = {}
            if self.cookies:
                headers["Cookie"] = self.cookies

            response = yield from aiohttp.request(self.method, url, data=data, headers=headers)
            body = (yield from response.read_and_close()).decode("utf-8")
            return response, body

    def send_request(self, payload):
        response, body = yield from self.send_raw_request(payload)
        self.requests_sent += 1
        return self.checker(response, body)

    def send_payload(self, payload):
        logger.debug("Sending payload %s", payload)
        query_data = self.get_query_data(self.injector.get_payload(payload))
        return (yield from self.send_request(query_data))

    def binary_search(self, expression, min=0, max=25):
        if (yield from self.send_payload(payload=expression > max)):
            return (yield from self.binary_search(expression, min=max, max=max * 2))

        while True:
            if max < min:
                return -1

            midpoint = (min + max) // 2

            if (yield from self.send_payload(payload=expression < midpoint)):
                max = midpoint - 1
            elif (yield from self.send_payload(payload=expression > midpoint)):
                min = midpoint + 1
            else:
                return midpoint

    def dumb_search(self, search_space, expression):
        for space in search_space:
            result = yield from self.send_payload(payload=expression == space)
            if result:
                return space
