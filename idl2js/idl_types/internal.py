from typing import Callable

from idl2js.builders.js import js_literal
from idl2js.generators.generator import ArrayGenerator, text
from idl2js.idl_types.base import IdlType


class InternalType(IdlType):
    """Base InternalType."""

    __generator__: Callable

    def generate(self):
        if self.is_sequence():
            return ArrayGenerator(
                element_generator=self.__generator__(self._builder_opt)(),
                min_size=2,
            ).generate()

        return self.__generator__(self._builder_opt)().generate()


class DOMString(InternalType):
    """String value that represents the same sequence of code units."""
    __internal__ = True
    __type__ = 'DOMString'
    __generator__ = text
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
    }


class USVString(InternalType):
    """Corresponds to the set of all possible sequences of unicode scalar values."""
    __internal__ = True
    __type__ = 'USVString'
    __generator__ = text
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
    }
