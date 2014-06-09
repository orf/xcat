import string
import asyncio

from . import BaseFeature
from ..xpath import substring_before, string_length


SEARCH_SPACE = string.ascii_letters + string.digits + " \n"


class EfficientSubstringSearch(BaseFeature):
    NAME = "Substring search speedup"
    TEST = [
        string_length(substring_before(SEARCH_SPACE, 'h')) == 7,
        string_length(substring_before(SEARCH_SPACE, 'o')) == 14
    ]

    @asyncio.coroutine
    def execute(self, requester, expression):
        # Small issue:
        # string-length(substring-before('abc','z')) == 0
        # string-length(substring-before('abc','a')) == 0
        # So we need to explicitly check if the expression is equal to the first char in our search space.
        # Not optimal, but still works out fairly efficient.

        if (yield from requester.send_payload(payload=expression == SEARCH_SPACE[0])):
            return SEARCH_SPACE[0]

        result = yield from requester.binary_search(
            expression=string_length(substring_before(SEARCH_SPACE, expression)),
            min=0,
            max=len(SEARCH_SPACE))
        if result == 0:
            return None
        else:
            return SEARCH_SPACE[result]