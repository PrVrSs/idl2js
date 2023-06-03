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


class Interface(IdlType):
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

    def build(self):
        pass

    @classmethod
    def dependencies(cls, attribute: str = 'self'):
        if attribute == 'self':
            return [
                argument.value.unwrap()
                for argument in cls._constructor_.arguments
            ]


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
        return f'{self.name}: {self.value}'


class IDLOptional:
    def __init__(self, value):
        self.value = value

    def unwrap(self):
        return self.value.unwrap()

    def __repr__(self):
        return f'FOptional[{self.value}]'


class IDLProperty:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name}: {self.value}'

class IDLType:
    def __init__(self, value):
        self.value = value

    def unwrap(self):
        return self.value

    def __repr__(self):
        return self.value


class IDLUnion:
    def __init__(self, items):
        self.items = items


class IDLSequence:
    def __init__(self, items):
        self.items = items

    @property
    def result(self):
        return self.items

    def __repr__(self):
        return f'FSequence[{self.items[0]}]'