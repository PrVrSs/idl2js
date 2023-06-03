from idl2js.builders.base import js_literal
from idl2js.generators.generator import CharGenerator
from idl2js.idl_types.base import IdlType


class DOMString(IdlType):
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


class USVString(IdlType):
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
