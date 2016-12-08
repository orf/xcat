from .algorithms import count, get_string, get_node_text, get_node_comments
from .display import XMLNode
from .requester import Requester
from .xpath import ROOT_NODE


async def get_nodes(requester: Requester, starting_path=ROOT_NODE):
    attributes = await get_node_attributes(requester, starting_path)
    child_node_count = await count(requester, starting_path.children)

    text_content = await get_node_text(requester, starting_path)
    comments = await get_node_comments(requester, starting_path)

    node_name = await get_string(requester, starting_path.name)

    return (XMLNode(name=node_name, attributes=attributes, text=text_content, comments=comments),
            [get_nodes(requester, starting_path=child) for child in starting_path.children(child_node_count)])


async def get_node_attributes(requester: Requester, node):
    attribute_count = await count(requester, node.attributes)

    async def _get_attributes_task(attr):
        name = await get_string(requester, attr.name)
        text = await get_string(requester, attr)
        return name, text

    results = [
        await _get_attributes_task(attr)
        for attr in node.attributes(attribute_count)
        ]

    return dict(results)
