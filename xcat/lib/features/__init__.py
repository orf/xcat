import asyncio

from ..xpath import Expression


class BaseFeature(object):
    NAME = None
    TEST = None

    @asyncio.coroutine
    def execute(self, requester, expression):
        raise NotImplementedError()

    @asyncio.coroutine
    def is_available(self, requester):
        if isinstance(self.TEST, Expression):
            tests = [self.TEST]
        elif isinstance(self.TEST, list):
            tests = self.TEST
        elif callable(self.TEST):
            tests = self.TEST()
        else:
            raise RuntimeError("TEST must be set to an xpath Expression, a list of Expressions or a callable")

        for t in tests:
            result = yield from requester.send_payload(
                payload=t
            )
            if not result:
                return False

        return True

from .substring_search import EfficientSubstringSearch
from .xpath_2 import XPath2
from .codepointsearch import CodepointSearch
from .oob_http import OOBDocFeature
from .entity_injection import EntityInjection
from .doc import DocFeature

_features = [
    XPath2,
    EfficientSubstringSearch,
    CodepointSearch,
    OOBDocFeature,
    EntityInjection,
    DocFeature
]


@asyncio.coroutine
def get_available_features(requester):
    feature_instances = [
        f() for f in _features
    ]
    futures = map(asyncio.Task, (f.is_available(requester) for f in feature_instances))
    results = (yield from asyncio.gather(*futures))
    return (feature_instances[i] for i, result in enumerate(results) if result is True)
