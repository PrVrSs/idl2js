import logging
from pathlib import Path
from pprint import pprint

from idl2js import InterfaceTarget, Transpiler


class Module(InterfaceTarget):
    kind = 'Module'


class Global(InterfaceTarget):
    kind = 'Global'


class Table(InterfaceTarget):
    kind = 'Table'


class Instance(InterfaceTarget):
    kind = 'Instance'


class Memory(InterfaceTarget):
    kind = 'Memory'


def main():
    logging.getLogger('idl2js').setLevel(logging.DEBUG)

    transpiler = Transpiler(
        idls=(
            str((Path(__file__).parent / 'webassembly.webidl').resolve()),  # https://webassembly.github.io/spec/js-api/#idl-index
        )
    )

    transpiler.transpile(
        targets=[
            Module,
            Global,
            Table,
            # Instance,
            Memory,
        ]
    )

    pprint(transpiler.js_instances)


if __name__ == '__main__':
    main()
