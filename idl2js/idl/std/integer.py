from idl2js.builders.js import js_literal
from idl2js.generators.generator import integer

from ..base import STDType
from .constants import (
    BYTE,
    INT_RANGES,
    LONG,
    LONG_LONG,
    OCTET,
    SHORT,
    UNSIGNED_LONG,
    UNSIGNED_LONG_LONG,
    UNSIGNED_SHORT,
)


class Integer(STDType):
    __internal__ = True


class Byte(Integer):
    __internal__ = True
    __type__ = BYTE
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[BYTE][0],
        'max_value': INT_RANGES[BYTE][1],
    }


class Octet(Integer):
    __internal__ = True
    __type__ = OCTET
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[OCTET][0],
        'max_value': INT_RANGES[OCTET][1],
    }


class Short(Integer):
    __internal__ = True
    __type__ = SHORT
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[SHORT][0],
        'max_value': INT_RANGES[SHORT][1],
    }


class UnsignedShort(Integer):
    __internal__ = True
    __type__ = UNSIGNED_SHORT
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[UNSIGNED_SHORT][0],
        'max_value': INT_RANGES[UNSIGNED_SHORT][1],
    }


class Long(Integer):
    __internal__ = True
    __type__ = LONG
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[LONG][0],
        'max_value': INT_RANGES[LONG][1],
    }


class UnsignedLong(Integer):
    __internal__ = True
    __type__ = UNSIGNED_LONG
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[UNSIGNED_LONG][0],
        'max_value': INT_RANGES[UNSIGNED_LONG][1],
    }


class LongLong(Integer):
    __internal__ = True
    __type__ = LONG_LONG
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[LONG_LONG][0],
        'max_value': INT_RANGES[LONG_LONG][1],
    }


class UnsignedLongLong(Integer):
    __internal__ = True
    __type__ = UNSIGNED_LONG_LONG
    __generator__ = integer
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': INT_RANGES[UNSIGNED_LONG_LONG][0],
        'max_value': INT_RANGES[UNSIGNED_LONG_LONG][1],
    }
