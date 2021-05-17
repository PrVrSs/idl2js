from functools import cached_property
from operator import attrgetter
from collections import deque

from more_itertools import flatten, first_true, first

from .built_in_types import BuiltInTypes
from .converter import convert
from .js.statements import create_literal, create_identifier


class DefinitionStorage:

    def __init__(self, idls):
        self._definitions = list(flatten(map(attrgetter('definitions'), idls)))

    @cached_property
    def build_definition(self):
        return [
            definition
            for definition in self._definitions
            if definition.type == 'interface' and definition.partial is False
        ]

    def find_by_type(self, idl_type):
        return first_true(self._definitions, pred=lambda definition: definition.name == idl_type)


class Builder:

    def __init__(self, std_types: BuiltInTypes, definition_storage: DefinitionStorage):
        self._std_types = std_types
        self._definition_storage = definition_storage

    def create(self, node):
        if node.idl_type.idl_type in self._std_types:
            return None, create_literal(self._std_types.generate(node.idl_type.idl_type))

        definition = self._definition_storage.find_by_type(node.idl_type.idl_type)
        converter = convert(builder=self, definition=definition)

        return converter, create_identifier(first(converter.variables).ast.expression.left.name)


def build(definition_storage, builder):
    for definition in definition_storage.build_definition:
        result = []

        todo = deque([convert(builder=builder, definition=definition)])
        while todo:
            item = todo.popleft()
            result.append(item.variables)
            todo.extendleft(item.dependencies)

        yield from flatten(reversed(result))
