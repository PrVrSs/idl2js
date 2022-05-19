from ..js.built_in.jtypes import PrimitiveType
from ..js.built_in.constants import BOOLEAN, LONG_LONG, UNSIGNED_LONG, UNSIGNED_LONG_LONG


class LongLong(PrimitiveType, name=LONG_LONG):
    pass


class UnsignedLongLong(PrimitiveType, name=UNSIGNED_LONG_LONG):
    pass


class UnsignedLong(PrimitiveType, name=UNSIGNED_LONG):
    pass


class Boolean(PrimitiveType, name=BOOLEAN):
    pass


class Any(PrimitiveType, name='any'):
    pass
