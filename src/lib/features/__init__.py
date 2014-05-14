from ..xpath.expression import Expression
import asyncio


class BaseFeature(object):
    NAME = None
    TEST = None

    @classmethod
    @asyncio.coroutine
    def is_available(cls, requester):
        if isinstance(cls.TEST, Expression):
            tests = [cls.TEST]
        elif isinstance(cls.TEST, list):
            tests = cls.TEST
        elif callable(cls.TEST):
            tests = cls.TEST()
        else:
            raise NotImplementedError("TEST must be set to an expression, a list of expressions or a callable")

        for t in tests:
            result = yield from requester.send_payload(
                payload=t
            )
            if not result:
                return False

        return True

from .substring_search import EfficientSubstringSearch
from .xpath_2 import XPath2
from .codepoints import Codepoints

_features = [
    XPath2,
    EfficientSubstringSearch,
    Codepoints
]


@asyncio.coroutine
def get_available_features(requester):
    futures = map(asyncio.Task, (f.is_available(requester) for f in _features))
    results = (yield from asyncio.gather(*futures))
    return (_features[i] for i, result in enumerate(results) if result is True)
