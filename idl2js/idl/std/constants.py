BYTE = 'byte'
OCTET = 'octet'
SHORT = 'short'
UNSIGNED_SHORT = 'unsigned short'
LONG = 'long'
UNSIGNED_LONG = 'unsigned long'
LONG_LONG = 'long long'
UNSIGNED_LONG_LONG = 'unsigned long long'

DOM_STRING = 'DOMString'
USV_STRING = 'USVString'
BYTE_STRING = 'ByteString'

BOOLEAN = 'boolean'

FLOAT = 'float'
UNRESTRICTED_FLOAT = 'unrestricted float'
DOUBLE = 'double'
UNRESTRICTED_DOUBLE = 'unrestricted double'


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

STRING = frozenset((
    DOM_STRING,
    USV_STRING,
    BYTE_STRING,
))


FLOATING = frozenset((
    FLOAT,
    UNRESTRICTED_FLOAT,
    DOUBLE,
    UNRESTRICTED_DOUBLE,
))

FLOAT_RANGES = {
    FLOAT: [-3.4028235e+38, 3.4028235e+38],
    UNRESTRICTED_FLOAT: [-3.4028235e+38, 3.4028235e+38],
    DOUBLE: [-1.7976931348623157e+308, 1.7976931348623157e+308],
    UNRESTRICTED_DOUBLE: [-1.7976931348623157e+308, 1.7976931348623157e+308],
}

INT_RANGES = {
    BYTE: [-2 ** 7, 2 ** 7 - 1],  # int8
    OCTET: [0, 2 ** 8 - 1],  # uint8
    SHORT: [-2 ** 15, 2 ** 15 - 1],  # int16
    UNSIGNED_SHORT: [0, 2 ** 16 - 1],  # uint16
    LONG: [-2 ** 31, 2 ** 31 - 1],  # int32
    UNSIGNED_LONG: [0, 2 ** 32 - 1],  # uint32
    LONG_LONG: [-2 ** 63, 2 ** 63 - 1],  # int64
    UNSIGNED_LONG_LONG: [0, 2 ** 64 - 1],  # uint64
}
