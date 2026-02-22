from idl2js.generators.chooser import Chooser
from idl2js.generators.context import clear_context, set_context
from idl2js.generators.rng import idl2js_random
from idl2js.generators.shrink import Shrinker
from idl2js.transpiler import Transpiler


class Fuzzer:
    def __init__(self, idls, coverage=None):
        self._transpiler = Transpiler(idls=idls)
        self._coverage = coverage

    def samples(self, idl_type, count=3, options=None):
        cdg = self._transpiler.build_cdg(idl_type, options)

        if self._coverage:
            set_context({'coverage': self._coverage})

        try:
            for _ in range(count):
                sample = cdg.sample()
                if self._coverage:
                    self._coverage.record_sample()
                yield sample
        finally:
            clear_context()

    def recorded_samples(self, idl_type, count=3, options=None, seed=None):
        """Generate samples while recording all random choices."""
        cdg = self._transpiler.build_cdg(idl_type, options)

        if self._coverage:
            set_context({'coverage': self._coverage})

        try:
            for _ in range(count):
                chooser = Chooser(seed=seed)
                idl2js_random.install(chooser)
                try:
                    sample = cdg.sample()
                finally:
                    idl2js_random.reset()

                if self._coverage:
                    self._coverage.record_sample()

                yield sample, chooser.choices
        finally:
            clear_context()

    def replay(self, idl_type, choices, options=None):
        """Replay a sample from a recorded choice sequence."""
        cdg = self._transpiler.build_cdg(idl_type, options)
        chooser = Chooser.from_choices(choices)
        idl2js_random.install(chooser)
        try:
            return cdg.sample()
        finally:
            idl2js_random.reset()

    def shrink(self, idl_type, choices, predicate, options=None):
        """Shrink a choice sequence while preserving predicate.

        Args:
            idl_type: the IDL type name to generate.
            choices: initial choice sequence known to satisfy predicate.
            predicate: callable(sample) -> bool, returns True if interesting.
            options: generation options.

        Returns:
            (minimal_sample, minimal_choices) tuple.
        """
        def test_fn(candidate_choices):
            try:
                sample = self.replay(idl_type, candidate_choices, options)
                return predicate(sample)
            except Exception:  # pylint: disable=broad-except
                return False

        shrinker = Shrinker(test_fn, choices)
        minimal_choices = shrinker.shrink()
        minimal_sample = self.replay(idl_type, minimal_choices, options)
        return minimal_sample, minimal_choices

    def generate_one_recorded(self, idl_type, options=None, seed=None):
        for sample, choices in self.recorded_samples(
            idl_type, count=1, options=options, seed=seed,
        ):
            return sample, choices
        return None, None  # pragma: no cover

    @property
    def coverage(self):
        return self._coverage
