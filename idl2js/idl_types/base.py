from collections import ChainMap
from typing import Any, Type

from idl2js.generators.generator import Generator


internal_types = {}


def _is_internal(ns: dict) -> bool:
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

    def __init__(self, builder_opt: dict | None = None):
        self._builder_opt = ChainMap(builder_opt or {}, self.__default_opt__)
        self._generator = self.__generator__(**self._builder_opt)

    def generate(self):
        return self._generator.generate()

    def build(self):
        return self.__builder__()

    @classmethod
    def dependencies(cls, attribute: str = 'self') -> list:
        return []
