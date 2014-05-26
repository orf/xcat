from .xpath1 import XPath1Executor
from ..features.codepointsearch import CodepointSearch


class XPath2Executor(XPath1Executor):

    def get_char(self, exp):
        if self.requester.has_feature(CodepointSearch):
            # Try and use the substring-before method to speed things up
            return self.requester.get_feature(CodepointSearch).execute(self.requester, exp)
        else:
            # Fallback to dumb searching
            return super().get_char(exp)