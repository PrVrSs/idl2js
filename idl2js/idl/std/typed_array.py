# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray#parameters

from idl2js.builders.js import js_interface

from ..base import STDType


class TypedArray(STDType):
    """Base TypedArray class."""


class Int8Array(TypedArray):
    __internal__ = True
    __type__ = 'Int8Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Int16Array(TypedArray):
    __internal__ = True
    __type__ = 'Int16Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Int32Array(TypedArray):
    __internal__ = True
    __type__ = 'Int32Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Uint8Array(TypedArray):
    __internal__ = True
    __type__ = 'Uint8Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Uint16Array(TypedArray):
    __internal__ = True
    __type__ = 'Uint16Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Uint32Array(TypedArray):
    __internal__ = True
    __type__ = 'Uint32Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Uint8ClampedArray(TypedArray):
    __internal__ = True
    __type__ = 'Uint8ClampedArray'
    __builder__ = js_interface

    __default_opt__ = {}


class BigInt64Array(TypedArray):
    __internal__ = True
    __type__ = 'BigInt64Array'
    __builder__ = js_interface

    __default_opt__ = {}


class BigUint64Array(TypedArray):
    __internal__ = True
    __type__ = 'BigUint64Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Float32Array(TypedArray):
    __internal__ = True
    __type__ = 'Float32Array'
    __builder__ = js_interface

    __default_opt__ = {}


class Float64Array(TypedArray):
    __internal__ = True
    __type__ = 'Float64Array'
    __builder__ = js_interface

    __default_opt__ = {}
