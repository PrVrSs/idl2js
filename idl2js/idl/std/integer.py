from idl2js.builders.js import js_literal
from idl2js.generators.generator import integer

from ..base import STDType
from .constants import INT_RANGES, LONG_LONG, UNSIGNED_LONG, UNSIGNED_LONG_LONG


class Integer(STDType):
    __internal__ = True


class Byte(Integer):
    pass


class Octet(Integer):
    pass


class Short(Integer):
    pass


class UnsignedShort(Integer):
    pass


class Long(Integer):
    pass


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
