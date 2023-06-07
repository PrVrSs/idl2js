from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class TypeFlag(IntEnum):
    NONE = 0
    OPTIONAL = 1
    SEQUENCE = 2

def get_base_type(idl_type):
    flags = TypeFlag.NONE

    while True:
        if isinstance(idl_type, IDLType):
            return idl_type.value, flags

        idl_type, flag = handle_type(idl_type)
        flags |= flag


class IDLFunction:
    def __init__(self, name, return_type, arguments=None):
        self.name = name
        self.arguments = arguments or []
        self.return_type = return_type

    def __repr__(self):
        return f'{self.name}({self.arguments})'


class IDLArgument:
    def __init__(self, name, value, const=None):
        self.name = name
        self.value = value
        self.const = const

    def __repr__(self):
        return f'Argument[{self.name}: {self.value}]'

class IDLProperty:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name}: {self.value}'


@dataclass
class IDLOptional:
    value: Any


@dataclass
class IDLType:
    value: Any


@dataclass
class IDLUnion:
    items: Any


@dataclass
class IDLSequence:
    items: Any


Type = IDLOptional | IDLType | IDLUnion | IDLSequence


def handle_type(idl_type: Type):
    match idl_type:
        case IDLSequence(items):
            return items[0], TypeFlag.SEQUENCE
        case IDLOptional(value):
            return value, TypeFlag.OPTIONAL
        case IDLType(value):
            return value, TypeFlag.NONE
        case IDLUnion(_):
            raise
        case _:
            raise
