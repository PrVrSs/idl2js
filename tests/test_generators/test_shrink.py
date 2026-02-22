import pytest

from idl2js.generators.chooser import ChoiceKind
from idl2js.generators.shrink import Shrinker


def make_int_choice(lo, hi, val):
    return (ChoiceKind.INTEGER, lo, hi, val)


def make_float_choice(lo, hi, val):
    return (ChoiceKind.FLOAT, lo, hi, val)


class TestShrinkerDeleteChoices:
    def test_removes_unnecessary_choices(self):
        choices = [
            make_int_choice(0, 100, 50),
            make_int_choice(0, 100, 30),
            make_int_choice(0, 100, 70),
        ]

        def predicate(c):
            return any(ch[3] >= 70 for ch in c)

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert len(result) <= len(choices)
        assert any(ch[3] >= 70 for ch in result)

    def test_empty_if_always_true(self):
        choices = [
            make_int_choice(0, 10, 5),
            make_int_choice(0, 10, 3),
        ]

        shrinker = Shrinker(lambda c: True, choices)
        result = shrinker.shrink()
        assert len(result) == 0

    def test_keeps_all_if_all_needed(self):
        choices = [
            make_int_choice(0, 100, 50),
            make_int_choice(0, 100, 60),
        ]

        def predicate(c):
            return (
                len(c) >= 2
                and c[0][3] >= 50
                and c[1][3] >= 60
            )

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert len(result) == 2


class TestShrinkerReduceIntegers:
    def test_reduces_large_integer(self):
        choices = [make_int_choice(0, 1000, 999)]

        def predicate(c):
            return len(c) == 1 and c[0][3] >= 10

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert result[0][3] <= 15

    def test_reduces_toward_zero(self):
        choices = [make_int_choice(-100, 100, 75)]

        def predicate(c):
            return len(c) == 1 and c[0][3] > 0

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert result[0][3] == 1

    def test_respects_range(self):
        choices = [make_int_choice(50, 100, 99)]

        def predicate(c):
            return len(c) == 1 and c[0][3] >= 50

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert result[0][3] == 50


class TestShrinkerShrinkFloats:
    def test_reduces_float_to_int(self):
        choices = [make_float_choice(0.0, 100.0, 42.7)]

        def predicate(c):
            return len(c) == 1 and c[0][3] >= 1.0

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert result[0][3] <= 42.7

    def test_reduces_toward_zero(self):
        choices = [make_float_choice(0.0, 100.0, 99.9)]

        def predicate(c):
            return len(c) == 1 and c[0][3] > 0

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()
        assert result[0][3] < 99.9


class TestShrinkerMaxSteps:
    def test_respects_max_steps(self):
        choices = [make_int_choice(0, 10000, i) for i in range(100)]

        shrinker = Shrinker(lambda c: len(c) > 0, choices, max_steps=10)
        shrinker.shrink()
        assert shrinker.steps <= 10


class TestShrinkerCombined:
    def test_deletes_and_reduces(self):
        choices = [
            make_int_choice(0, 100, 99),
            make_int_choice(0, 100, 50),
            make_int_choice(0, 100, 80),
        ]

        def predicate(c):
            return any(ch[3] >= 80 for ch in c)

        shrinker = Shrinker(predicate, choices)
        result = shrinker.shrink()

        assert len(result) <= 2
        assert any(ch[3] >= 80 for ch in result)
