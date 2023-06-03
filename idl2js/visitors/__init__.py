from ..exceptions import UnknownDefinitionType
from .interface import InterfaceVisitor
from .utils import DefinitionEnum


def make_idl_type_class(definition):
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
