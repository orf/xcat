import unittest

from .fake_requester import FakeRequestMaker
from .sources.lxml import LXMLTestSource
from ..xcat import run_then_return



class TestXPath1(unittest.TestCase):

    def test_injectors(self):
        request_maker = FakeRequestMaker(LXMLTestSource(
            "/test/node[@one='1{}']"
        ), lambda r, b: len(b))