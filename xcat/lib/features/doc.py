from . import BaseFeature
from ..xpath import document_uri, doc, E


class DocFeature(BaseFeature):
    NAME = "Read local XML files"

    def TEST(self):
        return [
            doc(document_uri(E("/"))) == E("/")
        ]