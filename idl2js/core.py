from pathlib import Path
from typing import Tuple

from idl2js.storage import Storage
from idl2js.converter import InterfaceTransformer
from idl2js.webidl.nodes import Ast as WebIDLAst
from idl2js.unparser import unparse
from idl2js.idl_processor import IDLProcessor
from idl2js.builder import Builder
from idl2js.built_in_types import BuiltInTypes


class Idl2Js:

    def __init__(self, idl: Tuple[str, ...], output: str):
        self._storage = Storage()
        self._std_types = BuiltInTypes()
        self._builder = Builder(storage=self._storage, std_types=self._std_types)
        self._idl_processor = IDLProcessor(idl)

        self._output = output

        self._make_variables()
        self._save('1.js')

    def _make_variables(self):
        InterfaceTransformer[WebIDLAst](
            storage=self._storage,
            builder=self._builder,
        ).visit(self._idl_processor.run()[0])

    def _save(self, file_name):
        with open(Path(self._output) / file_name, 'w') as f:
            f.write('\n'.join(self.generate()))

    def generate(self):
        return [
            unparse(variable.ast)
            for variable in self._storage._var
        ]


def main():
    raw_idl = (Path(__file__).parent.parent / 'blob.webidl').resolve()
    idl2js = Idl2Js(idl=(str(raw_idl),), output=str(Path('.output').resolve()))
    print(idl2js.generate())


if __name__ == '__main__':
    main()
