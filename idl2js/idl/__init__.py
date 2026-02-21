from ..exceptions import UnknownDefinitionType
from ..log import logger
from .definitions import (
    CallbackInterfaceVisitor,
    CallbackVisitor,
    DefinitionEnum,
    DictionaryVisitor,
    EnumVisitor,
    InterfaceVisitor,
    MixinVisitor,
    NamespaceVisitor,
    TypeDefVisitor,
)
from .std import (
    Any,
    ArrayBuffer,
    BigInt,
    Boolean,
    Byte,
    ByteString,
    DataView,
    DOMString,
    Double,
    Float,
    Float16Array,
    Int8Array,
    Long,
    LongLong,
    Object,
    Octet,
    SharedArrayBuffer,
    Short,
    Symbol,
    Undefined,
    UnsignedLong,
    UnsignedLongLong,
    UnsignedShort,
    UnrestrictedDouble,
    UnrestrictedFloat,
    USVString,
    Void,
)


def make_idl_type(definition):  # pylint: disable=too-many-return-statements
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
            return NamespaceVisitor().run(node=definition)
        case DefinitionEnum.CALLBACK:
            return CallbackVisitor().run(node=definition)
        case DefinitionEnum.CALLBACK_INTERFACE:
            return CallbackInterfaceVisitor().run(node=definition)
        case DefinitionEnum.INTERFACE_MIXIN:
            return MixinVisitor().run(node=definition)
        case DefinitionEnum.INCLUDES:
            return None
        case _:
            logger.warning('Unknown definition type: %s', definition.type)
            return None
