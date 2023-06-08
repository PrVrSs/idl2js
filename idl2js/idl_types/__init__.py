from idl2js.exceptions import UnknownDefinitionType
from idl2js.idl_types.interface import InterfaceVisitor
from idl2js.idl_types.internal import DOMString, USVString
from idl2js.idl_types.type_def import TypeDefVisitor
from idl2js.idl_types.utils import DefinitionEnum
from idl2js.idl_types.idl_enum import EnumVisitor


def make_idl_type(definition):
    match definition.type:
        case DefinitionEnum.INTERFACE:
            return InterfaceVisitor().run(node=definition)
        case DefinitionEnum.TYPEDEF:
            return TypeDefVisitor().run(node=definition)
        case DefinitionEnum.ENUM:
            return EnumVisitor().run(node=definition)
        case DefinitionEnum.DICTIONARY:
            raise
        case DefinitionEnum.NAMESPACE:
            raise
        case _:
            raise UnknownDefinitionType(f'Unknown {definition.type=}')
