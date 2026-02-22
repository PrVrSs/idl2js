from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .strategy import DEFAULT_WEIGHTS, GenerationStrategy


@dataclass
class CoverageTracker:
    _type_counts: Counter = field(default_factory=Counter)
    _enum_values: dict[str, set] = field(
        default_factory=lambda: defaultdict(set),
    )
    _value_classes: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set),
    )
    _strategy_counts: dict[str, Counter] = field(
        default_factory=lambda: defaultdict(Counter),
    )
    _array_sizes: dict[str, set[int]] = field(
        default_factory=lambda: defaultdict(set),
    )
    _total_samples: int = 0

    def record_type(self, type_name):
        self._type_counts[type_name] += 1

    def record_enum_value(self, type_name, value):
        self._enum_values[type_name].add(value)

    def record_value_class(self, type_name, value_class):
        self._value_classes[type_name].add(value_class)

    def record_strategy(self, type_name, strategy):
        self._strategy_counts[type_name][strategy] += 1

    def record_array_size(self, type_name, size):
        self._array_sizes[type_name].add(size)

    def record_sample(self):
        self._total_samples += 1

    def type_coverage(self, all_types):
        if not all_types:
            return 1.0
        covered = sum(1 for t in all_types if t in self._type_counts)
        return covered / len(all_types)

    def enum_coverage(self, type_name, all_values):
        if not all_values:
            return 1.0
        return len(self._enum_values[type_name]) / len(all_values)

    def uncovered_enum_values(self, type_name, all_values):
        return set(all_values) - self._enum_values[type_name]

    def suggest_weights(self, type_name):
        covered = self._value_classes.get(type_name, set())
        weights = dict(DEFAULT_WEIGHTS)

        if 'boundary' not in covered:
            weights[GenerationStrategy.BOUNDARY] = 0.5
            weights[GenerationStrategy.RANDOM] = 0.3
        elif 'special' not in covered:
            weights[GenerationStrategy.SPECIAL] = 0.4
            weights[GenerationStrategy.RANDOM] = 0.4

        return weights

    def reset(self):
        self._type_counts.clear()
        self._enum_values.clear()
        self._value_classes.clear()
        self._strategy_counts.clear()
        self._array_sizes.clear()
        self._total_samples = 0

    @property
    def total_samples(self):
        return self._total_samples

    def report(self):
        return {
            'total_samples': self._total_samples,
            'types_covered': len(self._type_counts),
            'type_distribution': dict(self._type_counts),
            'enum_coverage': {
                k: len(v) for k, v in self._enum_values.items()
            },
            'value_classes': {
                k: sorted(v) for k, v in self._value_classes.items()
            },
            'array_sizes': {
                k: sorted(v) for k, v in self._array_sizes.items()
            },
        }
