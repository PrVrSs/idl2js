from collections import ChainMap
from typing import Any, Type

from idl2js.generators.generator import Generator
from idl2js.idl_types.helper import TypeFlag


internal_types = {}


def _is_internal(ns: dict) -> bool:  # pylint: disable=invalid-name
    return ns.get('__internal__', False) is True


class MetaType(type):
    def __new__(mcs, typename, bases, ns):
        if not bases:
            return super().__new__(mcs, typename, bases, ns)

        cls = super().__new__(mcs, typename, bases, ns)
        if (idl_type := ns.get('__type__', None)) is not None and _is_internal(ns):
            internal_types[idl_type] = cls

        return cls



class IdlType(metaclass=MetaType):

    __internal__: bool
    __generator__: Type[Generator]
    __builder__:  Any
    __type__: str
    __default_opt__: dict

    def __init__(self, builder_opt: dict | None = None, flags: TypeFlag = TypeFlag.NONE):
        self._builder_opt = ChainMap(builder_opt or {}, self.__default_opt__)
        self._flags = flags

    def is_sequence(self):
        return bool(self._flags & TypeFlag.SEQUENCE)

    def is_optional(self):
        return bool(self._flags & TypeFlag.OPTIONAL)

    def build(self, *args, **kwargs):
        return self.__builder__(*args, **kwargs)

    @classmethod
    def dependencies(cls) -> list:
        return []
