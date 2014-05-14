from . import BaseFeature
import asyncio
from ..xpath.expression import lower_case


class XPath2(BaseFeature):
    NAME = "XPath Version"
    TEST = lower_case('A') == 'a'