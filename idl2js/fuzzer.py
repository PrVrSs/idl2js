from idl2js.transpiler import Transpiler


class Fuzzer:
    def __init__(self, idls):
        self._transpiler = Transpiler(idls=idls)

    def samples(self, idl_type, count = 3, options = None):
        cdg = self._transpiler.build_cdg(idl_type, options)

        for _ in range(count):
            yield cdg.sample()



def main():
    from pathlib import Path
    from pprint import pprint

    fuzzer = Fuzzer(
        idls=[
            str((Path(__file__).parent / 'webassembly.webidl').resolve()),
        ])

    pprint(list(fuzzer.samples(
        idl_type='Blob',
        options={
            'DOMString': {
                'min_codepoint': 70,
                'max_codepoint': 100,
            }
        }
    )))


if __name__ == '__main__':
    main()
