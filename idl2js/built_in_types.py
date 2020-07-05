import string
from random import randint, choice


BYTE = 'byte'
OCTET = 'octet'
SHORT = 'short'
UNSIGNED_SHORT = 'unsigned short'
LONG = 'long'
UNSIGNED_LONG = 'unsigned long'
LONG_LONG = 'long long'
UNSIGNED_LONG_LONG = 'unsigned long long'

DOM_STRING = 'DOMString'

INT = frozenset((
    BYTE,
    OCTET,
    SHORT,
    UNSIGNED_SHORT,
    LONG,
    UNSIGNED_LONG,
    LONG_LONG,
    UNSIGNED_LONG_LONG,
))


_INT_RANGES = {
    BYTE: [-2 ** 7, 2 ** 7 - 1],  # int8
    OCTET: [0, 2 ** 8 - 1],  # uint8
    SHORT: [-2 ** 15, 2 ** 15 - 1],  # int16
    UNSIGNED_SHORT: [0, 2 ** 16 - 1],  # uint16
    LONG: [-2 ** 31, 2 ** 31 - 1],  # int32
    UNSIGNED_LONG: [0, 2 ** 32 - 1],  # uint32
    LONG_LONG: [-2 ** 63, 2 ** 63 - 1],  # int64
    UNSIGNED_LONG_LONG: [0, 2 ** 64 - 1],  # uint64
}


class BuiltInTypes:

    def generate(self, type_):
        if type_ in INT:
            return self.generate_int(type_)
        elif type_ == DOM_STRING:
            return self.generate_string()

        return type_

    @staticmethod
    def generate_int(int_type):
        return randint(*_INT_RANGES[int_type])

    @staticmethod
    def generate_string():
        return ''.join(
            choice(string.ascii_lowercase)
            for _ in range(randint(1, 10))
        )
