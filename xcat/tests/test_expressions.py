import unittest

from ..lib.xpath import *


class TestExpressionMagic(unittest.TestCase):

    def test_sugar(self):
        e = Attribute("test")

        for expr, value in (
                (e == 1, "@test=1"),
                (e + 1, "@test+1"),
                (e != "lol", "@test!='lol'"),
                (e - 10, "@test-10"),
                (e <= (Attribute("lol") - 10), "@test<=(@lol-10)")):
            self.assertEqual(str(expr), value)