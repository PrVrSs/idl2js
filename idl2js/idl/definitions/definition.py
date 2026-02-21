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
    CALLBACK = 'callback'
    CALLBACK_INTERFACE = 'callback interface'
    INTERFACE_MIXIN = 'interface mixin'
    INCLUDES = 'includes'


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
    _inheritance_: str | None
    __builder__:  Any

    @classmethod
    def dependencies(cls):
        deps = [
            get_base_type(argument.value)
            for argument in cls._constructor_.arguments
        ]
        inheritance = getattr(cls, '_inheritance_', None)
        if inheritance:
            deps.append((inheritance, 0))
        return deps


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
    _inheritance_: str | None
    __builder__:  Any
    __generator__: Any

    @classmethod
    def dependencies(cls):
        deps = [
            get_base_type(argument.value)
            for argument in cls._attributes_
        ]
        inheritance = getattr(cls, '_inheritance_', None)
        if inheritance:
            deps.append((inheritance, 0))
        return deps

    def attr_name(self):
        return [attr.name for attr in self._attributes_]


class Callback_(DefinitionType):  # pylint: disable=invalid-name
    """Base Callback class."""

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__: Any

    @classmethod
    def dependencies(cls):
        return [
            get_base_type(argument.value)
            for argument in cls._constructor_.arguments
        ]


class Namespace_(DefinitionType):  # pylint: disable=invalid-name
    """Base Namespace class."""

    _attributes_: Any
    _constructor_: IDLFunction
    __builder__: Any

    @classmethod
    def dependencies(cls):
        deps = []
        for attr in cls._attributes_:
            if isinstance(attr, IDLFunction):
                for arg in attr.arguments:
                    deps.append(get_base_type(arg.value))
        return deps
