import math

import pytest

from idl2js.generators.chooser import ChoiceKind
from idl2js.generators.mutator import (
    mutate_array,
    mutate_choices,
    mutate_float,
    mutate_integer,
    mutate_string,
)


class TestMutateInteger:
    def test_returns_integer(self):
        for _ in range(100):
            result = mutate_integer(42)
            assert isinstance(result, int)

    def test_respects_bounds(self):
        for _ in range(100):
            result = mutate_integer(50, min_value=0, max_value=100)
            assert 0 <= result <= 100

    def test_produces_different_values(self):
        results = {mutate_integer(42) for _ in range(100)}
        assert len(results) > 1

    def test_zero(self):
        results = {mutate_integer(0) for _ in range(100)}
        assert len(results) > 1

    def test_boundary_values_appear(self):
        results = {mutate_integer(50, min_value=0, max_value=100)
                    for _ in range(1000)}
        assert 0 in results or 100 in results or 1 in results


class TestMutateFloat:
    def test_returns_number(self):
        for _ in range(100):
            result = mutate_float(1.0)
            assert isinstance(result, float)

    def test_produces_different_values(self):
        results = set()
        for _ in range(100):
            r = mutate_float(1.0)
            if not math.isnan(r):
                results.add(r)
        assert len(results) > 1

    def test_can_produce_special(self):
        results = set()
        for _ in range(1000):
            r = mutate_float(1.0)
            if math.isnan(r):
                results.add('nan')
            elif math.isinf(r):
                results.add('inf')
            else:
                results.add(r)
        assert 'nan' in results or 'inf' in results or 0.0 in results

    def test_respects_bounds_for_normal(self):
        for _ in range(100):
            result = mutate_float(0.5, min_value=0.0, max_value=1.0)
            if not math.isnan(result) and not math.isinf(result):
                assert 0.0 <= result <= 1.0


class TestMutateString:
    def test_returns_string(self):
        for _ in range(100):
            result = mutate_string('hello')
            assert isinstance(result, str)

    def test_empty_string(self):
        for _ in range(100):
            result = mutate_string('')
            assert isinstance(result, str)

    def test_produces_different_values(self):
        results = {mutate_string('hello') for _ in range(100)}
        assert len(results) > 1

    def test_single_char(self):
        results = {mutate_string('a') for _ in range(100)}
        assert len(results) > 1


class TestMutateArray:
    def test_returns_list(self):
        for _ in range(100):
            result = mutate_array([1, 2, 3])
            assert isinstance(result, list)

    def test_empty_array(self):
        result = mutate_array([])
        assert result == []

    def test_produces_different_results(self):
        results = {tuple(mutate_array([1, 2, 3])) for _ in range(100)}
        assert len(results) > 1

    def test_with_element_mutator(self):
        mutator = lambda x: x * 2
        results = set()
        for _ in range(100):
            r = mutate_array([1, 2, 3], element_mutator=mutator)
            results.add(tuple(r))
        assert len(results) > 1

    def test_single_element(self):
        results = {tuple(mutate_array([42])) for _ in range(100)}
        assert len(results) > 1


class TestMutateChoices:
    def test_same_length(self):
        choices = [
            (ChoiceKind.INTEGER, 0, 100, 50),
            (ChoiceKind.FLOAT, 0.0, 1.0, 0.5),
            (ChoiceKind.INTEGER, -10, 10, 0),
        ]
        result = mutate_choices(choices)
        assert len(result) == len(choices)

    def test_at_least_one_mutated(self):
        choices = [
            (ChoiceKind.INTEGER, 0, 100, 50),
            (ChoiceKind.INTEGER, 0, 100, 50),
            (ChoiceKind.INTEGER, 0, 100, 50),
        ]
        different = False
        for _ in range(100):
            result = mutate_choices(choices)
            if result != choices:
                different = True
                break
        assert different

    def test_respects_integer_bounds(self):
        choices = [(ChoiceKind.INTEGER, 10, 20, 15)] * 10
        for _ in range(100):
            result = mutate_choices(choices, mutation_rate=1.0)
            for kind, lo, hi, val in result:
                assert lo <= val <= hi

    def test_float_mutation(self):
        choices = [(ChoiceKind.FLOAT, 0.0, 1.0, 0.5)] * 5
        mutated_values = set()
        for _ in range(100):
            result = mutate_choices(choices, mutation_rate=1.0)
            for _, _, _, val in result:
                if not math.isnan(val) and not math.isinf(val):
                    mutated_values.add(round(val, 6))
        assert len(mutated_values) > 1

    def test_empty_input(self):
        result = mutate_choices([])
        assert result == []

    def test_num_mutations_param(self):
        choices = [(ChoiceKind.INTEGER, 0, 100, 50)] * 20
        result = mutate_choices(choices, num_mutations=1)
        diffs = sum(1 for a, b in zip(choices, result) if a != b)
        assert diffs >= 1

    def test_preserves_kind_and_bounds(self):
        choices = [
            (ChoiceKind.INTEGER, 5, 95, 50),
            (ChoiceKind.FLOAT, -1.0, 1.0, 0.0),
        ]
        result = mutate_choices(choices, mutation_rate=1.0)
        for (ok, olo, ohi, _), (nk, nlo, nhi, _) in zip(choices, result):
            assert ok == nk
            assert olo == nlo
            assert ohi == nhi

    def test_boolean_flip(self):
        choices = [(ChoiceKind.BOOLEAN, 0, 1, 0)] * 5
        result = mutate_choices(choices, mutation_rate=1.0)
        for _, _, _, val in result:
            assert val == 1
