from collections import deque
from typing import Optional

from .environment import Environment
from .idl_processor import process_idl
from .idl_types import make_idl_type
from .idl_types.base import internal_types


def convert_idl(idls):
    return [
        make_idl_type(definition)
        for idl in process_idl(idls)
        for definition in idl.definitions
    ]


def external_types(idls: list[str]):
    return {
        idl_type.__type__: idl_type
        for idl_type in convert_idl(idls)
    }


class CDGNode:
    def __init__(self, idl_type):
        self.idl_type = idl_type
        self.children = []

        self.deps = []

    def build(self):
        self.deps = [
            child.build()
            for child in self.children
        ]

        return self.idl_type().build([dep.name for dep in self.deps])

class CDG:
    def __init__(self, root):
        self.root = root

    def sample(self):
        result = [self.root.build()]
        todo = deque([self.root])

        while todo:
            node = todo.popleft()
            result.extend(node.deps[::-1])
            todo.extend(node.children)

        return result[::-1]

class Transpiler:
    def __init__(self, idls: Optional[tuple[str, ...]] = None):
        self.environment = Environment({
            **internal_types,
            **external_types(idls or []),
        })

    def build_cdg(self, idl_type):
        node = CDGNode(self.environment.get_type(idl_type))
        cdg = CDG(root=node)
        todo = deque([node])
        while todo:
            item = todo.popleft()

            for dependency in item.idl_type.dependencies():
                new_node = CDGNode(self.environment.get_type(dependency))
                item.children.append(new_node)
                todo.append(new_node)

        return cdg
