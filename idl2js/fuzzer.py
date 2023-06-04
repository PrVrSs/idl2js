from idl2js.transpiler import Transpiler


class Statistic:
    pass


class Fuzzer:
    def __init__(self, transpiler: Transpiler):
        self._transpiler = transpiler
        self._statistic = Statistic()

    def run(self, idl_type, samples = 3):
        cdg = self._transpiler.build_cdg(idl_type)

        for _ in range(samples):
            yield cdg.sample()



def main():
    from pathlib import Path
    from pprint import pprint

    target = (Path(__file__).parent / 'webassembly.webidl').resolve()

    transpiler = Transpiler(idls=[str(target)])
    fuzzer = Fuzzer(transpiler=transpiler)

    pprint(list(fuzzer.run(idl_type='Blob')))


if __name__ == '__main__':
    main()
