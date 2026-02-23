import math
from collections import ChainMap
from enum import IntEnum
from typing import Any, Callable, Type

from idl2js.generators.context import get_coverage
from idl2js.generators.generator import ArrayGenerator, Generator
from idl2js.generators.rng import idl2js_random


internal_types = {}


class TypeFlag(IntEnum):
    NONE = 0
    OPTIONAL = 1
    SEQUENCE = 2
    NULLABLE = 4


def _is_std(ns: dict) -> bool:  # pylint: disable=invalid-name
    return ns.get('__internal__', False) is True


class MetaType(type):
    def __new__(mcs, typename, bases, ns):
        if not bases:
            return super().__new__(mcs, typename, bases, ns)

        cls = super().__new__(mcs, typename, bases, ns)
        if (idl_type := ns.get('__type__', None)) is not None and _is_std(ns):
            internal_types[idl_type] = cls

        return cls


class IdlType(metaclass=MetaType):

    __internal__: bool
    __generator__: Type[Generator]
    __builder__:  Any
    __type__: str
    __default_opt__: dict

    def __init__(self, builder_opt: dict | None = None, flags: TypeFlag = TypeFlag.NONE):
        self._builder_opt = ChainMap(builder_opt or {}, self.__default_opt__)
        self._flags = flags

    def is_sequence(self):
        return bool(self._flags & TypeFlag.SEQUENCE)

    def is_optional(self):
        return bool(self._flags & TypeFlag.OPTIONAL)

    def is_nullable(self):
        return bool(self._flags & TypeFlag.NULLABLE)

    def build(self, *args, **kwargs):
        return self.__builder__(*args, **kwargs)

    @classmethod
    def dependencies(cls) -> list:
        return []


class STDType(IdlType):
    """Base STDType."""

    __generator__: Callable

    def generate(self):
        coverage = get_coverage()

        if self.is_nullable() and idl2js_random.random() < 0.2:
            if coverage:
                coverage.record_type(self.__type__)
                coverage.record_value_class(self.__type__, 'null')
            return None

        result = self._generate_value()

        if coverage:
            coverage.record_type(self.__type__)
            self._record_coverage(coverage, result)

        return result

    def _generate_value(self):
        if self.is_sequence():
            return ArrayGenerator(
                element_generator=self.__generator__(self._builder_opt)(),
                min_size=2,
            ).generate()

        return self.__generator__(self._builder_opt)().generate()

    def _record_coverage(self, coverage, result):
        if isinstance(result, list):
            coverage.record_array_size(self.__type__, len(result))
            coverage.record_value_class(self.__type__, 'sequence')
        elif isinstance(result, int) and not isinstance(result, bool):
            self._record_int_coverage(coverage, result)
        elif isinstance(result, float):
            self._record_float_coverage(coverage, result)
        elif isinstance(result, str):
            self._record_str_coverage(coverage, result)
        elif isinstance(result, bool):
            value_class = f'bool_{result}'
            coverage.record_value_class(self.__type__, value_class)
        else:
            coverage.record_value_class(self.__type__, 'other')

    def _record_int_coverage(self, coverage, result):
        min_val = self._builder_opt.get('min_value')
        max_val = self._builder_opt.get('max_value')

        if result == 0:
            coverage.record_value_class(self.__type__, 'zero')
        elif min_val is not None and result == min_val:
            coverage.record_value_class(self.__type__, 'boundary')
        elif max_val is not None and result == max_val:
            coverage.record_value_class(self.__type__, 'boundary')
        elif result in (1, -1):
            coverage.record_value_class(self.__type__, 'special')
        else:
            coverage.record_value_class(self.__type__, 'random')

    def _record_float_coverage(self, coverage, result):
        if math.isnan(result):
            coverage.record_value_class(self.__type__, 'nan')
        elif math.isinf(result):
            coverage.record_value_class(self.__type__, 'infinity')
        elif result == 0.0:
            coverage.record_value_class(self.__type__, 'zero')
        else:
            coverage.record_value_class(self.__type__, 'random')

    def _record_str_coverage(self, coverage, result):
        if not result:
            coverage.record_value_class(self.__type__, 'empty_string')
        elif len(result) == 1:
            coverage.record_value_class(self.__type__, 'single_char')
        else:
            coverage.record_value_class(self.__type__, 'random')
