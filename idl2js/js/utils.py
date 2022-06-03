from attr import fields

from .nodes import ast_node_map


def is_simple(data):
    return isinstance(data, (int, float, str))


def from_json(data):
    if isinstance(data, list):
        return [from_json(item) for item in data]

    if is_simple(data):
        return data

    ast_node = ast_node_map[data['type']]
    return ast_node(**{
        field.name: from_json(data[field.name])
        for field in fields(ast_node)
        if field.name in (set(data) - {'raw'})
    })
