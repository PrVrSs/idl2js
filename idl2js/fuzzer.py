from idl2js.transpiler import Transpiler


class Fuzzer:
    def __init__(self, idls):
        self._transpiler = Transpiler(idls=idls)

    def samples(self, idl_type, count = 3, options = None):
        cdg = self._transpiler.build_cdg(idl_type, options)

        for _ in range(count):
            yield cdg.sample()
