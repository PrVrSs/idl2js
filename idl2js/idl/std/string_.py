from idl2js.builders.js import js_literal
from idl2js.generators.generator import text

from ..base import STDType


class String(STDType):
    """Base String class."""


class DOMString(String):
    """String value that represents the same sequence of code units."""
    __internal__ = True
    __type__ = 'DOMString'
    __generator__ = text
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
    }


class USVString(String):
    """Corresponds to the set of all possible sequences of unicode scalar values."""
    __internal__ = True
    __type__ = 'USVString'
    __generator__ = text
    __builder__ = js_literal

    __default_opt__ = {
        'min_codepoint': 0,
        'max_codepoint': 128,
    }
