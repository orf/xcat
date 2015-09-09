from . import Source
from lxml import etree


class LXMLTestSource(Source):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open("data.xml") as fd:
            self.tree = etree.parse(fd)

    def execute_query(self, payload):
        results = self.tree.xpath(self.query.format(payload))
        return len(results) != 0