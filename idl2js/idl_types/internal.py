from typing import Type

from idl2js.builders.js import js_literal
from idl2js.generators.generator import CharGenerator, Generator
from idl2js.idl_types.base import IdlType


class InternalType(IdlType):
    """Base InternalType."""

    __generator__: Type[Generator]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generator = self.__generator__(**self._builder_opt)

    def generate(self):
        return self._generator.generate()


class DOMString(InternalType):
    """String value that represents the same sequence of code units."""
    __internal__ = True
    __type__ = 'DOMString'
    __generator__ = CharGenerator
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
        'include_categories': {'Lu'},
    }


class USVString(InternalType):
    """Corresponds to the set of all possible sequences of unicode scalar values."""
    __internal__ = True
    __type__ = 'USVString'
    __generator__ = CharGenerator
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
        'include_categories': {'Lu'},
    }