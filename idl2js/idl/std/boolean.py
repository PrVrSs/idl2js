from idl2js.builders.js import js_literal
from idl2js.generators.generator import boolean

from ..base import STDType
from .constants import BOOLEAN


class Boolean(STDType):
    __internal__ = True
    __type__ = BOOLEAN
    __generator__ = boolean
    __builder__ = js_literal

    __default_opt__ = {}
