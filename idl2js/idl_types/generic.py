from collections import ChainMap
from typing import Any, Type

from idl2js.generators.generator import Generator
from idl2js.idl_types.base import IdlType


class GenericType(IdlType):
    """Base GenericType."""


class Interface(GenericType):
    """Base Interface class."""

    _builder_opt_ = {
        'instance_property': tuple(),
        'instance_method': tuple(),
        'include_attribute': tuple(),
    }

    _attributes_: Any
    _constructor_: Any
    __builder__: Type[Generator]

    def __init__(self, builder_opt: dict | None = None):
        self._builder_opt = ChainMap(builder_opt or {}, self.__default_opt__)

    def generate(self):
        return self._generator.generate()

    def build(self, arguments = None, name = None):
        return self.__builder__(arguments or [], name)

    @classmethod
    def dependencies(cls, attribute: str = 'self'):
        if attribute == 'self':
            return cls._constructor_.arguments

        return cls._attributes_