from collections import deque

from idl2js.generators.chooser import Chooser, ChoiceKind
from idl2js.generators.rng import idl2js_random
from idl2js.idl.std.constants import FLOAT_RANGES, INT_RANGES
from idl2js.smt.predicates import OraclePredicate
from idl2js.smt.solver import SMTSolver


# Strategy selection: random() returns float in [0, 1].
# With DEFAULT_WEIGHTS (RANDOM=0.5, BOUNDARY=0.3, SPECIAL=0.2),
# r <= 0.5 → RANDOM. We inject 0.1 to force RANDOM strategy.
_FORCE_RANDOM_STRATEGY = 0.1


class GuidedChooser(Chooser):
    """Chooser that injects solved values by matching type ranges.

    Forces RANDOM strategy for all generation, then intercepts
    ``randint(lo, hi)`` / ``uniform(lo, hi)`` calls where the range
    matches a target IDL type, returning the SMT-solved value from a queue.
    """

    def __init__(self, int_queues=None, float_queues=None, seed=None):
        super().__init__(seed=seed)
        self._int_queues = {k: deque(v) for k, v in (int_queues or {}).items()}
        self._float_queues = {k: deque(v) for k, v in (float_queues or {}).items()}

    def random(self):
        # Force RANDOM strategy by always returning a low value.
        # This ensures integer/float generators use randint/uniform with
        # the full type range, which we can then intercept.
        if self._int_queues or self._float_queues:
            value = _FORCE_RANDOM_STRATEGY
            self._choices.append((ChoiceKind.FLOAT, 0.0, 1.0, value))
            return value
        return super().random()

    def randint(self, a, b):
        key = (a, b)
        if key in self._int_queues and self._int_queues[key]:
            value = self._int_queues[key].popleft()
            value = max(a, min(b, int(value)))
            self._choices.append((ChoiceKind.INTEGER, a, b, value))
            return value
        return super().randint(a, b)

    def uniform(self, a, b):
        key = (a, b)
        if key in self._float_queues and self._float_queues[key]:
            value = self._float_queues[key].popleft()
            value = max(a, min(b, float(value)))
            self._choices.append((ChoiceKind.FLOAT, a, b, value))
            return value
        return super().uniform(a, b)


def _build_queues(predicate, solution):
    """Build range-keyed value queues from an SMT solution.

    Maps each field's IDL type range to the solved value.
    """
    int_queues = {}
    float_queues = {}

    for field_name, idl_type in predicate.fields.items():
        if field_name not in solution:
            continue
        value = solution[field_name]

        if idl_type in INT_RANGES:
            lo, hi = INT_RANGES[idl_type]
            int_queues.setdefault((lo, hi), []).append(value)
        elif idl_type in FLOAT_RANGES:
            lo, hi = FLOAT_RANGES[idl_type]
            float_queues.setdefault((lo, hi), []).append(value)

    return int_queues, float_queues


def guided_samples(fuzzer, idl_type, predicate, count=10, options=None):
    """Generate samples with SMT-guided values for oracle-relevant fields.

    For each sample:
    1. Solve the predicate to get concrete values
    2. Force RANDOM strategy so generators use full-range calls
    3. Intercept those calls and inject the solved values

    Yields:
        (sample, choices) tuples where each sample satisfies the predicate.
    """
    solver = SMTSolver(predicate)
    solutions = solver.solve_many(count)

    if not solutions:
        yield from fuzzer.recorded_samples(idl_type, count=count, options=options)
        return

    transpiler = fuzzer._transpiler
    for solution in solutions:
        int_queues, float_queues = _build_queues(predicate, solution)
        chooser = GuidedChooser(
            int_queues=int_queues,
            float_queues=float_queues,
        )
        idl2js_random.install(chooser)
        try:
            cdg = transpiler.build_cdg(idl_type, options)
            sample = cdg.sample()
            yield sample, chooser.choices
        finally:
            idl2js_random.reset()
