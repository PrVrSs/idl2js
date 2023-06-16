from collections import deque
from pathlib import Path
from typing import Optional

from .environment import Environment
from .idl import make_idl_type
from .idl.base import internal_types
from .idl_processor import process_idl


COMMON_DEFINITION = Path(__file__).parent.resolve() / 'common_definitions.webidl'


def common_definition():
    return {
        idl_type.__type__: idl_type
        for idl_type in convert_idl([COMMON_DEFINITION])
    }


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


class Option:
    def __init__(self, option):
        self._option = option or {}

    def __call__(self, idl_type):
        return self._option.get(idl_type.__type__, {})


class CDGNode:
    def __init__(self, idl_type, flags):
        self.idl_type = idl_type
        self.children = []
        self.flags = flags

        self.dependencies = []

    def build(self, option):
        self.dependencies = [
            child.build(option)
            for child in self.children
        ]

        return self.idl_type(option(self.idl_type), self.flags).build([
                dependency.name
                for dependency in self.dependencies
            ],
        )


class CDG:
    def __init__(self, root, options):
        self.root = root
        self.options = options or {}

    def sample(self):
        result = [self.root.build(self.options)]
        todo = deque([self.root])

        while todo:
            node = todo.popleft()
            result.extend(node.dependencies[::-1])
            todo.extend(node.children)

        return result[::-1]


class Transpiler:
    def __init__(self, idls: Optional[tuple[str, ...]] = None):
        self.environment = Environment({
            **internal_types,
            **common_definition(),
            **external_types(idls or []),
        })

    def build_cdg(self, idl_type, options):
        node = CDGNode(self.environment.get_type(idl_type), 0)
        cdg = CDG(root=node, options=Option(options))
        todo = deque([node])
        while todo:
            item = todo.popleft()

            for dependency, flags in item.idl_type.dependencies():
                if dependency == 'any':
                    type_ = self.environment.get_random_type()
                else:
                    type_ = self.environment.get_type(dependency)

                new_node = CDGNode(type_, flags)
                item.children.append(new_node)
                todo.append(new_node)

        return cdg
