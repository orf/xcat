import xml
from ..lib.requests.requester import RequestMaker


class FakeRequestMaker(RequestMaker):
    def __init__(self, source, checker, features=None, injector=None):
        super().__init__(None, None, None, checker, features, injector)
        self.source = source

    def send_raw_request(self, data):
        return None, self.source.execute_query(data)