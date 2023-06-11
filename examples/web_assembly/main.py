import logging
from pathlib import Path
from pprint import pprint

from idl2js import Fuzzer


def main():
    logging.getLogger('idl2js').setLevel(logging.DEBUG)

    fuzzer = Fuzzer(
        idls=(
            str((Path(__file__).parent / 'webassembly.webidl').resolve()),  # https://webassembly.github.io/spec/js-api/#idl-index
        )
    )

    pprint(list(fuzzer.samples(idl_type='MemoryDescriptor')))


if __name__ == '__main__':
    main()
