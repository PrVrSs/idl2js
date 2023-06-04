from enum import Enum

from idl2js.idl_types.helper import IDLSequence, IDLType, IDLUnion


class DefinitionEnum(str, Enum):
    INTERFACE = 'interface'
    TYPEDEF = 'typedef'
    ENUM = 'enum'
    DICTIONARY = 'dictionary'
    NAMESPACE = 'namespace'


def prepare_idl_type(idl_type):
    if isinstance(idl_type, list):
        return [prepare_idl_type(idl) for idl in idl_type]

    if isinstance(idl_type, str):
        return IDLType(value=idl_type)

    if idl_type.generic == 'sequence':
        return IDLSequence(items=prepare_idl_type(idl_type.idl_type))

    if idl_type.union is True:
        return IDLUnion(items=[prepare_idl_type(idl_t) for idl_t in idl_type.idl_type])

    return IDLType(value=idl_type.idl_type)
