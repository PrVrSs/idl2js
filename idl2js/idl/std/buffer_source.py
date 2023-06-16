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
