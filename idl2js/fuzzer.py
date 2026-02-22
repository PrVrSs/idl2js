from idl2js.generators.context import clear_context, set_context
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

    @property
    def coverage(self):
        return self._coverage
