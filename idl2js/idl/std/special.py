from idl2js.builders.js import js_literal
from idl2js.generators.generator import (
    any_type,
    bigint,
    object_type,
    symbol,
    undefined,
)

from ..base import STDType


class Undefined(STDType):
    """The undefined type has a unique value."""
    __internal__ = True
    __type__ = 'undefined'
    __generator__ = undefined
    __builder__ = js_literal

    __default_opt__ = {}


class Void(STDType):
    """Legacy alias for undefined."""
    __internal__ = True
    __type__ = 'void'
    __generator__ = undefined
    __builder__ = js_literal

    __default_opt__ = {}


class Any(STDType):
    """The any type is the union of all other types."""
    __internal__ = True
    __type__ = 'any'
    __generator__ = any_type
    __builder__ = js_literal

    __default_opt__ = {}


class Object(STDType):
    """The object type corresponds to the set of all possible object references."""
    __internal__ = True
    __type__ = 'object'
    __generator__ = object_type
    __builder__ = js_literal

    __default_opt__ = {}


class Symbol(STDType):
    """The symbol type corresponds to the set of all possible Symbol values."""
    __internal__ = True
    __type__ = 'symbol'
    __generator__ = symbol
    __builder__ = js_literal

    __default_opt__ = {}


class BigInt(STDType):
    """The bigint type corresponds to the set of all possible BigInt values."""
    __internal__ = True
    __type__ = 'bigint'
    __generator__ = bigint
    __builder__ = js_literal

    __default_opt__ = {}
