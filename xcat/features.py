from collections import namedtuple
from typing import List

from xcat.xpath.xpath_3 import available_environment_variables, unparsed_text_available
from .algorithms import ASCII_SEARCH_SPACE
from .requester import Requester
from .xpath import F, E
from .xpath.xpath_1 import string_length, substring_before, function_available, boolean, string
from .xpath.xpath_2 import string_to_codepoints, lower_case, exists, document_uri, current_date_time, doc, doc_available

Feature = namedtuple('Feature', 'name tests')


features = [
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
    Feature('xpath-2',
            [
                lower_case('A') == 'a'
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
            ])

]


async def detect_features(requester: Requester) -> List[Feature]:
    returner = []

    for feature in features:
        checks = [await requester.check(test) for test in feature.tests]
        if all(checks):
            returner.append(feature)

    return returner
