from ..exceptions import UnknownDefinitionType
from ..log import logger
from .definitions import (
    DefinitionEnum,
    DictionaryVisitor,
    EnumVisitor,
    InterfaceVisitor,
    TypeDefVisitor,
)
from .std import ArrayBuffer, DOMString, Int8Array, LongLong, UnsignedLong, USVString


def make_idl_type(definition):
    match definition.type:
        case DefinitionEnum.INTERFACE:
            return InterfaceVisitor().run(node=definition)
        case DefinitionEnum.TYPEDEF:
            return TypeDefVisitor().run(node=definition)
        case DefinitionEnum.ENUM:
            return EnumVisitor().run(node=definition)
        case DefinitionEnum.DICTIONARY:
            return DictionaryVisitor().run(node=definition)
        case DefinitionEnum.NAMESPACE:
            logger.warning(f'Not implemented {DefinitionEnum.NAMESPACE}')
            return None
        case _:
            raise UnknownDefinitionType(f'Unknown {definition.type=}')
