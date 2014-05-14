from . import BaseFeature
from ..xpath.expression import substring_before, string_length
import string

SEARCH_SPACE = string.ascii_letters + string.digits + " \n"


class EfficientSubstringSearch(BaseFeature):
    NAME = "Substring string search speedup"
    TEST = [
        string_length(substring_before(SEARCH_SPACE, 'h')) == 7,
        string_length(substring_before(SEARCH_SPACE, 'o')) == 14
    ]

    @staticmethod
    def execute(requester, expression):
        result = yield from requester.binary_search(
            expression=string_length(substring_before(SEARCH_SPACE, expression)),
            min=0,
            max=len(SEARCH_SPACE))
        return SEARCH_SPACE[result]