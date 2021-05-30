from pathlib import Path

from idl2js.storage import Storage
from idl2js.unparser import unparse
from idl2js.idl_processor import process_idl
from idl2js.js.statements import try_statement
from idl2js.built_in_types import BuiltInTypes
from idl2js.builder import Builder, DefinitionStorage, build


class Idl2Js:

    def __init__(self, idl: tuple[str, ...]):
        self._storage = Storage()
        self._std_types = BuiltInTypes()
        self._prepared_idl = process_idl(idl)
        self._definition_storage = DefinitionStorage(self._prepared_idl)

        self._builder = Builder(
            std_types=self._std_types,
            definition_storage=self._definition_storage,
        )

    def generate(self):
        return [
            unparse(try_statement(variable.ast))
            for variable in build(self._definition_storage, self._builder)
        ]


def main():
    # pylint: disable=import-outside-toplevel
    from pprint import pprint
    raw_idl = (Path(__file__).parent.parent / 'webidl' / 'blob.webidl').resolve()
    raw_idl2 = (Path(__file__).parent.parent / 'webidl' / 'BlobEvent.webidl').resolve()
    idl2js = Idl2Js(idl=(str(raw_idl), str(raw_idl2)))
    pprint(idl2js.generate(), width=220)


if __name__ == '__main__':
    main()
