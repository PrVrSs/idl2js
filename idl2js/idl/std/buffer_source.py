from idl2js.builders.js import js_interface

from ..base import STDType


class Buffer(STDType):
    """Base Buffer class."""


class ArrayBuffer(Buffer):
    """ArrayBuffer."""
    __internal__ = True
    __type__ = 'ArrayBuffer'
    __builder__ = js_interface

    __default_opt__ = {}


class SharedArrayBuffer(Buffer):
    """SharedArrayBuffer."""
    __internal__ = True
    __type__ = 'SharedArrayBuffer'
    __builder__ = js_interface

    __default_opt__ = {}


class DataView(Buffer):
    """DataView."""
    __internal__ = True
    __type__ = 'DataView'
    __builder__ = js_interface

    __default_opt__ = {}
