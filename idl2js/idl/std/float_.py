from idl2js.builders.js import js_literal
from idl2js.generators.generator import float_

from ..base import STDType
from .constants import (
    DOUBLE,
    FLOAT,
    FLOAT_RANGES,
    UNRESTRICTED_DOUBLE,
    UNRESTRICTED_FLOAT,
)


class Floating(STDType):
    __internal__ = True


class Float(Floating):
    __internal__ = True
    __type__ = FLOAT
    __generator__ = float_
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': FLOAT_RANGES[FLOAT][0],
        'max_value': FLOAT_RANGES[FLOAT][1],
    }


class UnrestrictedFloat(Floating):
    __internal__ = True
    __type__ = UNRESTRICTED_FLOAT
    __generator__ = float_
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': FLOAT_RANGES[UNRESTRICTED_FLOAT][0],
        'max_value': FLOAT_RANGES[UNRESTRICTED_FLOAT][1],
    }


class Double(Floating):
    __internal__ = True
    __type__ = DOUBLE
    __generator__ = float_
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': FLOAT_RANGES[DOUBLE][0],
        'max_value': FLOAT_RANGES[DOUBLE][1],
    }


class UnrestrictedDouble(Floating):
    __internal__ = True
    __type__ = UNRESTRICTED_DOUBLE
    __generator__ = float_
    __builder__ = js_literal

    __default_opt__ = {
        'min_value': FLOAT_RANGES[UNRESTRICTED_DOUBLE][0],
        'max_value': FLOAT_RANGES[UNRESTRICTED_DOUBLE][1],
    }
