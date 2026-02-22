import math
from enum import Enum, auto

from .rng import idl2js_random


class GenerationStrategy(Enum):
    RANDOM = auto()
    BOUNDARY = auto()
    SPECIAL = auto()


DEFAULT_WEIGHTS = {
    GenerationStrategy.RANDOM: 0.5,
    GenerationStrategy.BOUNDARY: 0.3,
    GenerationStrategy.SPECIAL: 0.2,
}


def select_strategy(weights=None):
    weights = weights or DEFAULT_WEIGHTS

    strategies = list(weights.keys())
    total = sum(weights.values())

    r = idl2js_random.random() * total
    cumulative = 0
    for strategy in strategies:
        cumulative += weights[strategy]
        if r <= cumulative:
            return strategy

    return strategies[-1]


def integer_boundary_values(min_value, max_value):
    candidates = {min_value, max_value, min_value + 1, max_value - 1, 0, 1, -1}

    for exp in range(1, 64):
        power = 1 << exp
        candidates.update([power, power - 1, -power, -power + 1])

    return sorted(v for v in candidates if min_value <= v <= max_value)


def float_boundary_values(min_value, max_value):
    candidates = [
        0.0,
        -0.0,
        1.0,
        -1.0,
        min_value,
        max_value,
        min_value / 2,
        max_value / 2,
    ]

    for exp in [-308, -100, -10, -1, 0, 1, 10, 100, 308]:
        try:
            val = 10.0 ** exp
            candidates.extend([val, -val])
        except OverflowError:
            pass

    return [v for v in candidates if min_value <= v <= max_value]


FLOAT_SPECIAL_VALUES = [math.nan, math.inf, -math.inf, -0.0]


def array_edge_sizes(min_size, max_size):
    candidates = {0, 1, min_size, max_size, max_size + 5}
    return sorted(v for v in candidates if 0 <= v)
