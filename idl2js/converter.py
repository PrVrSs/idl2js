from typing import Type

from .js.statements import (
    create_attribute,
    create_object,
    create_operation,
    create_dict,
    create_property,
)
from .js.variable import Variable as JsVariable, create_js_variable
from .visitor import Visitor
from .utils import unique_name
from .webidl.nodes import (
    Ast as WebIDLAst,
    Attribute,
    Constructor,
    Definition,
    Dictionary,
    Interface,
    Operation,
)


class Converter(Visitor[WebIDLAst]):

    def __init__(self, builder):
        self.variables: list[JsVariable] = []
        self.dependencies: list[Converter] = []

        self._builder = builder

    def _calculate_node(self, node: WebIDLAst):
        dependency, property_ = self._builder.create(node)

        if dependency is not None:
            self.dependencies.append(dependency)

        return property_


class DictionaryConverter(Converter):

    def visit_dictionary(self, node: Dictionary) -> None:
        self.variables.append(
            create_js_variable(
                type_=node.name,
                ast=create_dict(
                    name=unique_name(),
                    properties=[
                        create_property(
                            key=member.name,  # type: ignore
                            value=self._calculate_node(node=member),
                        )
                        for member in node.members
                    ]
                )
            )
        )


class InterfaceConverter(Converter):

    def __init__(self, builder):
        super().__init__(builder=builder)

        self._type = None
        self._name = None

    def visit_interface(self, node: Interface) -> None:
        if node.partial is True:
            return

        self._type = node.name
        self._name = unique_name()

        self.generic_visit(node)

    def visit_constructor(self, node: Constructor) -> None:
        self.variables.append(
            create_js_variable(
                type_=self._type,
                ast=create_object(
                    name=self._name,
                    progenitor=self._type,
                    arguments=[
                        self._calculate_node(node=argument)
                        for argument in node.arguments
                    ],
                ),
            )
        )

        self.generic_visit(node)

    def visit_attribute(self, node: Attribute) -> None:
        self.variables.append(
            create_js_variable(
                type_=node.idl_type.idl_type,  # type: ignore
                ast=create_attribute(
                    name=unique_name(),
                    progenitor=self._name,
                    method=node.name
                ),
            )
        )

        self.generic_visit(node)

    def visit_operation(self, node: Operation) -> None:
        self.variables.append(
            create_js_variable(
                type_=node.idl_type.idl_type,  # type: ignore
                ast=create_operation(
                    name=unique_name(),
                    progenitor=self._name,
                    method=node.name,
                    arguments=[
                        self._calculate_node(node=argument)
                        for argument in node.arguments
                    ],
                )
            )
        )

        self.generic_visit(node)


CONVERTER_MAP: dict[str, Type[Converter]] = {
    'dictionary': DictionaryConverter,
    'interface': InterfaceConverter,
}


def convert(builder, definition: Definition) -> Converter:
    return (
        (converter := CONVERTER_MAP[definition.type](builder=builder)).visit(definition) or
        converter
    )
