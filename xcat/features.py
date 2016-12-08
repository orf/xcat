from collections import namedtuple
from typing import List

from .algorithms import binary_search, ASCII_SEARCH_SPACE
from .requester import Requester
from .xpath.xpath_1 import string_length, substring_before

Feature = namedtuple('Feature', 'name tests function')


async def substring_search(requester: Requester, expression):
    # Small issue:
    # string-length(substring-before('abc','z')) == 0
    # string-length(substring-before('abc','a')) == 0
    # So we need to explicitly check if the expression is equal to the first char in our search space.
    # Not optimal, but still works out fairly efficient.

    if await requester.check(expression == ASCII_SEARCH_SPACE[0]):
        return ASCII_SEARCH_SPACE[0]

    result = await binary_search(
        requester,
        string_length(substring_before(ASCII_SEARCH_SPACE, expression)),
        min=0,
        max=len(ASCII_SEARCH_SPACE))
    if result == 0:
        return None
    else:
        return ASCII_SEARCH_SPACE[result]


features = [
    Feature('substring-search',
            [
                string_length(substring_before(ASCII_SEARCH_SPACE, 'h')) == 7,
                string_length(substring_before(ASCII_SEARCH_SPACE, 'o')) == 14
            ],
            substring_search)
]


async def detect_features(requester: Requester) -> List[Feature]:
    returner = []

    for feature in features:
        checks = [await requester.check(test) for test in feature.tests]
        if all(checks):
            returner.append(feature)

    return returner
