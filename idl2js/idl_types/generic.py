from typing import Any

from idl2js.idl_types.base import IdlType
from idl2js.idl_types.helper import IDLFunction, get_base_type


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

    @classmethod
    def dependencies(cls):
        return [
            get_base_type(argument.value)
            for argument in cls._constructor_.arguments
        ]


class TypeDef(GenericType):
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


class Enum_(GenericType):
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


class Dictionary(GenericType):
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
