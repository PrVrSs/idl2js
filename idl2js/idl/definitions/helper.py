from dataclasses import dataclass
from typing import Any

from idl2js.exceptions import IDL2JSException
from idl2js.generators.rng import idl2js_random

from ..base import TypeFlag


def get_base_type(idl_type):
    flags = TypeFlag.NONE

    while True:
        if isinstance(idl_type, IDLType):
            return idl_type.value, flags

        idl_type, flag = handle_type(idl_type)
        flags |= flag


class IDLFunction:
    def __init__(self, name, return_type, arguments=None, static=False):
        self.name = name
        self.arguments = arguments or []
        self.return_type = return_type
        self.static = static

    def __repr__(self):
        return f'{self.name}({self.arguments})'


class IDLArgument:
    def __init__(self, name, value, const=None, default=None):
        self.name = name
        self.value = value
        self.const = const
        self.default = default

    def __repr__(self):
        return f'Argument[{self.name}: {self.value}]'


class IDLProperty:
    def __init__(self, name, value, static=False, readonly=False):
        self.name = name
        self.value = value
        self.static = static
        self.readonly = readonly

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


@dataclass
class IDLNullable:
    value: Any


@dataclass
class IDLPromise:
    value: Any


@dataclass
class IDLRecord:
    key: Any
    value: Any


@dataclass
class IDLFrozenArray:
    items: Any


@dataclass
class IDLVariadic:
    value: Any


IdlTypeAlias = IDLOptional | IDLType | IDLSequence | IDLNullable | IDLPromise | IDLRecord \
    | IDLFrozenArray | IDLVariadic


def handle_type(idl_type: IdlTypeAlias):  # pylint: disable=too-many-return-statements
    match idl_type:
        case IDLSequence(items):
            return items[0], TypeFlag.SEQUENCE
        case IDLFrozenArray(items):
            return items[0], TypeFlag.SEQUENCE
        case IDLOptional(value):
            return value, TypeFlag.OPTIONAL
        case IDLNullable(value):
            return value, TypeFlag.NULLABLE
        case IDLPromise(value):
            return value, TypeFlag.NONE
        case IDLRecord(key=_, value=value):
            return value, TypeFlag.NONE
        case IDLVariadic(value):
            return value, TypeFlag.SEQUENCE
        case IDLType(value):
            return value, TypeFlag.NONE
        case IDLUnion(items):
            return idl2js_random.choice(items), TypeFlag.NONE
        case _:
            raise IDL2JSException


def prepare_idl_type(idl_type):  # pylint: disable=too-many-return-statements
    if isinstance(idl_type, list):
        return [prepare_idl_type(idl) for idl in idl_type]

    if isinstance(idl_type, str):
        return IDLType(value=idl_type)

    generic = getattr(idl_type, 'generic', None)

    if generic == 'sequence':
        return IDLSequence(items=prepare_idl_type(idl_type.idl_type))

    if generic == 'Promise':
        inner = prepare_idl_type(idl_type.idl_type)
        return IDLPromise(value=inner[0] if isinstance(inner, list) else inner)

    if generic == 'record':
        parts = prepare_idl_type(idl_type.idl_type)
        return IDLRecord(key=parts[0], value=parts[1])

    if generic in ('FrozenArray', 'ObservableArray'):
        return IDLFrozenArray(items=prepare_idl_type(idl_type.idl_type))

    if idl_type.union is True:
        return IDLUnion(items=[prepare_idl_type(idl_t) for idl_t in idl_type.idl_type])

    result = IDLType(value=idl_type.idl_type)

    if getattr(idl_type, 'nullable', False):
        result = IDLNullable(value=result)

    return result
