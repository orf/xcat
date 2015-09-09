

class Source(object):
    def __init__(self, vulnerable_query):
        self.query = vulnerable_query

    def execute_query(self, payload):
        raise NotImplementedError()
