from . import BaseFeature
from ..xpath import lower_case


class XPath2(BaseFeature):
    NAME = "XPath 2"
    TEST = lower_case('A') == 'a'