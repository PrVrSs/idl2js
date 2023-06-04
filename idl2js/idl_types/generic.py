from collections import ChainMap
from enum import IntEnum, auto
from typing import Any, Type

from idl2js.idl_types.base import IdlType
from idl2js.idl_types.helper import IDLFunction, get_base_type


class Constrains(IntEnum):
    OPTIONAL = auto()


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
    _constructor_: IDLFunction
    __builder__:  Any

    def __init__(self, builder_opt: dict | None = None):
        self._builder_opt = ChainMap(builder_opt or {}, self.__default_opt__)

    def generate(self):
        return self._generator.generate()

    def build(self, arguments = None, name = None):
        return self.__builder__(arguments or [], name)

    @classmethod
    def dependencies(cls, attribute: str = 'self'):
        if attribute == 'self':
            return [
                get_base_type(argument)
                for argument in cls._constructor_.arguments
            ]

        return cls._attributes_
