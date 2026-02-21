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


def _classify_definitions(all_definitions):
    includes = []
    partials = []
    non_partials = []

    for definition in all_definitions:
        if definition.type == 'includes':
            includes.append(definition)
        elif getattr(definition, 'partial', False):
            partials.append(definition)
        else:
            non_partials.append(definition)

    return non_partials, partials, includes


def _merge_attributes(target, source):
    target_attrs = list(getattr(target, '_attributes_', []))
    source_attrs = list(getattr(source, '_attributes_', []))
    target._attributes_ = target_attrs + source_attrs  # pylint: disable=protected-access


def convert_idl(idls):  # pylint: disable=too-many-locals
    all_definitions = [
        definition
        for idl in process_idl(idls)
        for definition in idl.definitions
    ]

    non_partials, partials, includes = _classify_definitions(all_definitions)

    types_dict = {}
    for definition in non_partials:
        idl_type = make_idl_type(definition)
        if idl_type is not None:
            types_dict[idl_type.__type__] = idl_type

    for definition in partials:
        idl_type = make_idl_type(definition)
        if idl_type is None:
            continue
        base = types_dict.get(idl_type.__type__)
        if base is not None:
            _merge_attributes(base, idl_type)
        else:
            types_dict[idl_type.__type__] = idl_type

    for inc in includes:
        target_name = getattr(inc, 'target', None)
        mixin_name = getattr(inc, 'includes', None)
        if not target_name or not mixin_name:
            continue

        target = types_dict.get(target_name)
        mixin = types_dict.get(mixin_name)
        if target is not None and mixin is not None:
            _merge_attributes(target, mixin)

    return list(types_dict.values())


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
