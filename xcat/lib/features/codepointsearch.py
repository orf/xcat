from . import BaseFeature
from ..xpath import string_to_codepoints


class CodepointSearch(BaseFeature):
    NAME = "String to codepoints"
    TEST = [
        string_to_codepoints("test")[1] == 116,
        string_to_codepoints("test")[2] == 101,
        string_to_codepoints("test")[3] == 115,
        string_to_codepoints("test")[4] == 116,
    ]

    def execute(self, requester, expression):
        result = yield from requester.binary_search(
            expression=string_to_codepoints(expression),
            min=0,
            max=255)
        if result == 0:
            return None
        else:
            return chr(result)