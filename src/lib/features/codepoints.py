from . import BaseFeature
from ..xpath.expression import string_to_codepoints


class Codepoints(BaseFeature):
    NAME = "String to codepoints"
    TEST = [
        string_to_codepoints("test")[1] == 116,
        string_to_codepoints("test")[2] == 101,
        string_to_codepoints("test")[3] == 115,
        string_to_codepoints("test")[4] == 116,
    ]