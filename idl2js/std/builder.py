import string
from random import randint, choice

from .integer import Any, Boolean, LongLong, UnsignedLong, UnsignedLongLong
from .string import USVString, DOMString
from ..js.built_in.constants import INT_RANGES, UNSIGNED_LONG, UNSIGNED_LONG_LONG, LONG_LONG


def generate_int(int_type):
    return randint(*INT_RANGES[int_type])


def generate_string():
    return ''.join(
        choice(string.ascii_lowercase)
        for _ in range(randint(1, 10))
    )


def generate_bool():
    return choice([True, False])


class STDBuilder:
    def build(self, type_):
        match type_:
            case LongLong():
                return generate_int(LONG_LONG)
            case UnsignedLongLong():
                return generate_int(UNSIGNED_LONG_LONG)
            case UnsignedLong():
                return generate_int(UNSIGNED_LONG)
            case DOMString():
                return generate_string()
            case USVString():
                return generate_string()
            case Boolean():
                return generate_bool()
            case Any():
                return generate_string()
            case _:
                raise TypeError('Unsupported')
