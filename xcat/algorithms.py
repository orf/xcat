import string

from .requester import Requester
from .xpath import xpath_1

ASCII_SEARCH_SPACE = string.digits + string.ascii_letters + '+./:@_ -,()!'
MISSING_CHARACTER = "?"


async def count(requester: Requester, expression, func=xpath_1.count):
    return await binary_search(requester, func(expression), min=0)


async def get_char(requester: Requester, expression):
    if requester.features['substring-search']:
        from .features import substring_search
        return await substring_search(requester, expression)
    else:
        # Dumb search
        for space in ASCII_SEARCH_SPACE:
            if await requester.check(expression == space):
                return space


async def get_string(requester: Requester, expression):
    is_empty_str_expression = xpath_1.string_length(xpath_1.normalize_space(expression)) == 0

    if await requester.check(is_empty_str_expression):
        return ""

    string_length = await count(requester, expression, func=xpath_1.string_length)

    if string_length <= 10:
        # Try common strings we've got before
        for common_name, _ in requester.counters['common-names'].most_common(5):
            if await requester.check(expression == common_name):
                return common_name

    chars = [
        await get_char(requester, xpath_1.substring(expression, i, 1))
        for i in range(1, string_length + 1)
        ]

    result = "".join(
        char if char is not None else MISSING_CHARACTER
        for char in chars
    )

    if len(result) <= 10:
        requester.counters['common-names'][result] += 1

    return result

async def get_node_text(requester: Requester, expression):
    text_node_count = await count(requester, expression.text)

    text_contents = [
        await get_string(requester, expr)
        for expr in expression.text(text_node_count)
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
