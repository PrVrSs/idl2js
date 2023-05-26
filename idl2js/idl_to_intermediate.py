from more_itertools import first_true
from pywebidl2.expr import Argument
from pywebidl2.expr import Ast as WebIDLAst
from pywebidl2.expr import (
    Constructor,
    Definition,
    Dictionary,
    Enum,
    Field,
    Interface,
    Namespace,
    Typedef,
)

from .intermediate.ftypes import (
    FArgument,
    FConst,
    FDictionary,
    FFunction,
    FInterface,
    FOptional,
    FSequence,
    FType,
    FUnion,
)
from .visitor import Visitor


def prepare_idl_type(idl_type):
    if isinstance(idl_type, list):
        return [prepare_idl_type(idl) for idl in idl_type]

    if isinstance(idl_type, str):
        return FType(value=idl_type)

    if idl_type.generic == 'sequence':
        return FSequence(items=prepare_idl_type(idl_type.idl_type))

    if idl_type.union is True:
        return FUnion(items=[prepare_idl_type(idl_t) for idl_t in idl_type.idl_type])

    return FType(value=idl_type.idl_type)


class InterfaceTransformation(Visitor[WebIDLAst]):
    def visit_interface(self, node: Interface):
        constructor = [self.visit(member) for member in node.members][0]

        interface = FInterface(
            name=node.name,
            attributes={'constructor': constructor},
            namespace=(
                namespace := first_true(
                    node.ext_attrs,
                    pred=lambda attr: attr.name == 'LegacyNamespace',
                )
            ) and namespace.rhs.value
        )

        return interface

    def visit_constructor(self, node: Constructor) -> None:
        return FFunction(
            name=node.type,
            return_type='self',
            arguments=[self.visit(argument) for argument in node.arguments],
        )

    def visit_argument(self, node: Argument):
        argument_type = prepare_idl_type(node.idl_type)

        if node.optional is True:
            argument_type = FOptional(value=argument_type)

        return FArgument(
            name=node.name,
            value=argument_type,
        )


class TypeDefTransformation(Visitor[WebIDLAst]):
    def visit_typedef(self, node: Typedef) -> FUnion:
        return FUnion(items=prepare_idl_type(node.idl_type.idl_type))


class EnumTransformation(Visitor[WebIDLAst]):
    def visit_enum(self, node: Enum) -> FUnion:
        return FUnion(items=[FConst(value=value.value)for value in node.values])


class DictionaryTransformation(Visitor[WebIDLAst]):
    def visit_dictionary(self, node: Dictionary) -> FDictionary:
        return FDictionary(items=[self.visit(member) for member in node.members])

    def visit_field(self, node: Field) -> FArgument:
        return FArgument(
            name=node.name,
            value=prepare_idl_type(node.idl_type),
        )


class NamespaceTransformation(Visitor[WebIDLAst]):
    def visit_namespace(self, node: Namespace) -> FDictionary:
        return


def _transform_from_idl_to_intermediate(definition: Definition):
    match definition.type:
        case 'interface':
            return InterfaceTransformation().visit(node=definition)
        case 'typedef':
            return TypeDefTransformation().visit(node=definition)
        case 'enum':
            return EnumTransformation().visit(node=definition)
        case 'dictionary':
            return DictionaryTransformation().visit(node=definition)
        case 'namespace':
            return NamespaceTransformation().visit(node=definition)
        case _:
            raise NotImplementedError(f'Not implement {definition.type=}')


def transform_from_idl_to_intermediate(definitions):
    return {
        name: _transform_from_idl_to_intermediate(definition)
        for name, definition in definitions.items()
    }
