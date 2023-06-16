from enum import Enum
from typing import Any

from ..base import IdlType
from .helper import IDLFunction, get_base_type


class DefinitionEnum(str, Enum):
    INTERFACE = 'interface'
    TYPEDEF = 'typedef'
    ENUM = 'enum'
    DICTIONARY = 'dictionary'
    NAMESPACE = 'namespace'


class DefinitionType(IdlType):
    """Base DefinitionType."""


class Interface(DefinitionType):
    """Base Interface class."""

    _builder_opt_ = {
        'instance_property': tuple(),
        'instance_method': tuple(),
        'include_attribute': tuple(),
    }

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__:  Any

    @classmethod
    def dependencies(cls):
        return [
            get_base_type(argument.value)
            for argument in cls._constructor_.arguments
        ]


class TypeDef(DefinitionType):
    """Base TypeDef class."""

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__:  Any
    __generator__: Any

    @classmethod
    def dependencies(cls):
        return [(cls.__generator__([
            get_base_type(argument)[0]
            for argument in cls._attributes_
        ]).generate(), 0)]


class Enum_(DefinitionType):  # pylint: disable=invalid-name
    """Base Enum class."""

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__:  Any
    __generator__: Any

    def generate(self):
        return self.__generator__([
            get_base_type(argument)[0]
            for argument in self._attributes_
        ]).generate()


class Dictionary(DefinitionType):
    """Base Dictionary class."""

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__:  Any
    __generator__: Any

    @classmethod
    def dependencies(cls):
        return [
            get_base_type(argument.value)
            for argument in cls._attributes_
        ]

    def attr_name(self):
        return [attr.name for attr in self._attributes_]
