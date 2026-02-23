import math

import pytest

from idl2js.generators.generator import (
    ArrayGenerator,
    BigIntGenerator,
    BooleanGenerator,
    CharGenerator,
    ChoiceGenerator,
    FloatGenerator,
    IntegerGenerator,
    TextGenerator,
)
from idl2js.generators.strategy import GenerationStrategy


class TestIntegerGeneratorStrategies:
    def test_random_in_range(self):
        gen = IntegerGenerator(
            min_value=0, max_value=100,
            strategy=GenerationStrategy.RANDOM,
        )
        for _ in range(100):
            result = gen.generate()
            assert 0 <= result <= 100

    def test_boundary_produces_boundaries(self):
        gen = IntegerGenerator(
            min_value=-128, max_value=127,
            strategy=GenerationStrategy.BOUNDARY,
        )
        results = {gen.generate() for _ in range(1000)}
        assert -128 in results
        assert 127 in results
        assert 0 in results

    def test_special_produces_special(self):
        gen = IntegerGenerator(
            min_value=-128, max_value=127,
            strategy=GenerationStrategy.SPECIAL,
        )
        results = {gen.generate() for _ in range(100)}
        assert results.issubset({0, 1, -1})

    def test_auto_strategy_varies(self):
        gen = IntegerGenerator(min_value=-128, max_value=127)
        results = {gen.generate() for _ in range(1000)}
        assert len(results) > 5
        assert -128 in results or 127 in results or 0 in results


class TestFloatGeneratorStrategies:
    def test_random_in_range(self):
        gen = FloatGenerator(
            min_value=0.0, max_value=1.0,
            strategy=GenerationStrategy.RANDOM,
        )
        for _ in range(100):
            result = gen.generate()
            assert 0.0 <= result <= 1.0

    def test_boundary_produces_boundaries(self):
        gen = FloatGenerator(
            min_value=-10.0, max_value=10.0,
            strategy=GenerationStrategy.BOUNDARY,
        )
        results = {gen.generate() for _ in range(1000)}
        assert -10.0 in results or 10.0 in results or 0.0 in results

    def test_unrestricted_special_produces_nan_inf(self):
        gen = FloatGenerator(
            min_value=-1.0, max_value=1.0,
            unrestricted=True,
            strategy=GenerationStrategy.SPECIAL,
        )
        has_nan = False
        has_inf = False
        for _ in range(1000):
            result = gen.generate()
            if math.isnan(result):
                has_nan = True
            if math.isinf(result):
                has_inf = True
        assert has_nan
        assert has_inf

    def test_restricted_special_no_nan_inf(self):
        gen = FloatGenerator(
            min_value=-1.0, max_value=1.0,
            unrestricted=False,
            strategy=GenerationStrategy.SPECIAL,
        )
        for _ in range(100):
            result = gen.generate()
            assert not math.isnan(result)
            assert not math.isinf(result)


class TestArrayGeneratorStrategies:
    def test_boundary_sizes(self):
        element_gen = IntegerGenerator(min_value=0, max_value=10)
        gen = ArrayGenerator(
            element_generator=element_gen,
            min_size=2, max_size=10,
            strategy=GenerationStrategy.BOUNDARY,
        )
        sizes = {len(gen.generate()) for _ in range(100)}
        assert 0 in sizes or 1 in sizes or 10 in sizes

    def test_special_sizes(self):
        element_gen = IntegerGenerator(min_value=0, max_value=10)
        gen = ArrayGenerator(
            element_generator=element_gen,
            min_size=2, max_size=10,
            strategy=GenerationStrategy.SPECIAL,
        )
        sizes = {len(gen.generate()) for _ in range(100)}
        assert 0 in sizes or 15 in sizes


class TestTextGeneratorStrategies:
    def test_special_strings(self):
        char_gen = CharGenerator(min_codepoint=0, max_codepoint=128)
        gen = TextGenerator(
            element_generator=char_gen,
            min_size=2, max_size=10,
            strategy=GenerationStrategy.SPECIAL,
        )
        results = {gen.generate() for _ in range(100)}
        assert '' in results

    def test_boundary_lengths(self):
        char_gen = CharGenerator(min_codepoint=0, max_codepoint=128)
        gen = TextGenerator(
            element_generator=char_gen,
            min_size=2, max_size=10,
            strategy=GenerationStrategy.BOUNDARY,
        )
        lengths = {len(gen.generate()) for _ in range(100)}
        assert 0 in lengths or 1 in lengths or 10 in lengths


class TestChoiceGeneratorCoverage:
    def test_basic_choice(self):
        gen = ChoiceGenerator(elements=['a', 'b', 'c'])
        results = {gen.generate() for _ in range(100)}
        assert results == {'a', 'b', 'c'}

    def test_coverage_guided_prefers_uncovered(self):
        gen = ChoiceGenerator(elements=['a', 'b', 'c'], coverage=True)
        first_three = [gen.generate() for _ in range(3)]
        assert set(first_three) == {'a', 'b', 'c'}


class TestBigIntGeneratorStrategies:
    def test_boundary_produces_boundaries(self):
        gen = BigIntGenerator(strategy=GenerationStrategy.BOUNDARY)
        results = {gen.generate() for _ in range(1000)}
        assert 0 in results or 1 in results or -1 in results

    def test_special_produces_special(self):
        gen = BigIntGenerator(strategy=GenerationStrategy.SPECIAL)
        results = {gen.generate() for _ in range(100)}
        assert results.issubset({0, 1, -1})
