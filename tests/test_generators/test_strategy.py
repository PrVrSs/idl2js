import pytest

from idl2js.generators.strategy import (
    FLOAT_SPECIAL_VALUES,
    GenerationStrategy,
    array_edge_sizes,
    float_boundary_values,
    integer_boundary_values,
    select_strategy,
)


class TestIntegerBoundaryValues:
    def test_includes_min_max(self):
        values = integer_boundary_values(-128, 127)
        assert -128 in values
        assert 127 in values

    def test_includes_adjacent_to_boundaries(self):
        values = integer_boundary_values(-128, 127)
        assert -127 in values
        assert 126 in values

    def test_includes_zero_and_unit(self):
        values = integer_boundary_values(-128, 127)
        assert 0 in values
        assert 1 in values
        assert -1 in values

    def test_includes_powers_of_two(self):
        values = integer_boundary_values(0, 255)
        for power in [2, 4, 8, 16, 32, 64, 128]:
            assert power in values

    def test_includes_powers_of_two_minus_one(self):
        values = integer_boundary_values(0, 255)
        for power in [1, 3, 7, 15, 31, 63, 127, 255]:
            assert power in values

    def test_filters_out_of_range(self):
        values = integer_boundary_values(0, 10)
        assert all(0 <= v <= 10 for v in values)

    def test_unsigned_range(self):
        values = integer_boundary_values(0, 65535)
        assert 0 in values
        assert 65535 in values
        assert -1 not in values

    def test_sorted(self):
        values = integer_boundary_values(-1000, 1000)
        assert values == sorted(values)


class TestFloatBoundaryValues:
    def test_includes_zero(self):
        values = float_boundary_values(-1.0, 1.0)
        assert 0.0 in values

    def test_includes_unit(self):
        values = float_boundary_values(-10.0, 10.0)
        assert 1.0 in values
        assert -1.0 in values

    def test_includes_boundaries(self):
        values = float_boundary_values(-5.0, 5.0)
        assert -5.0 in values
        assert 5.0 in values

    def test_filters_out_of_range(self):
        values = float_boundary_values(0.0, 1.0)
        assert all(0.0 <= v <= 1.0 for v in values)


class TestFloatSpecialValues:
    def test_has_nan(self):
        import math
        assert any(math.isnan(v) for v in FLOAT_SPECIAL_VALUES)

    def test_has_infinity(self):
        import math
        assert math.inf in FLOAT_SPECIAL_VALUES
        assert -math.inf in FLOAT_SPECIAL_VALUES


class TestArrayEdgeSizes:
    def test_includes_zero(self):
        sizes = array_edge_sizes(2, 10)
        assert 0 in sizes

    def test_includes_one(self):
        sizes = array_edge_sizes(2, 10)
        assert 1 in sizes

    def test_includes_max(self):
        sizes = array_edge_sizes(2, 10)
        assert 10 in sizes

    def test_sorted(self):
        sizes = array_edge_sizes(2, 10)
        assert sizes == sorted(sizes)


class TestSelectStrategy:
    def test_returns_valid_strategy(self):
        for _ in range(100):
            strategy = select_strategy()
            assert isinstance(strategy, GenerationStrategy)

    def test_custom_weights(self):
        weights = {GenerationStrategy.BOUNDARY: 1.0}
        for _ in range(10):
            assert select_strategy(weights) == GenerationStrategy.BOUNDARY

    def test_all_strategies_reachable(self):
        seen = set()
        for _ in range(1000):
            seen.add(select_strategy())
        assert seen == set(GenerationStrategy)
