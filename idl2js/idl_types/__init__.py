from idl2js.exceptions import UnknownDefinitionType
from idl2js.idl_types.interface import InterfaceVisitor
from idl2js.idl_types.internal import DOMString, USVString
from idl2js.idl_types.utils import DefinitionEnum


def make_idl_type(definition):
    match definition.type:
        case DefinitionEnum.INTERFACE:
            return InterfaceVisitor().run(node=definition)
        case DefinitionEnum.TYPEDEF:
            raise
        case DefinitionEnum.ENUM:
            raise
        case DefinitionEnum.DICTIONARY:
            raise
        case DefinitionEnum.NAMESPACE:
            raise
        case _:
            raise UnknownDefinitionType(f'Unknown {definition.type=}')
