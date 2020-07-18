from pathlib import Path

from idl2js.storages import VariableStorage
from idl2js.webidl import parse as parse_webidl
from idl2js.converter import InterfaceTransformer
from idl2js.webidl.nodes import Ast as WebIDLAst
from idl2js.unparser import unparse


class Idl2Js:

    def __init__(self, webild):
        self._variable_store = VariableStorage()

        self._make_variables(webild)

    def _make_variables(self, webidl):
        InterfaceTransformer[WebIDLAst](
            variable_storage=self._variable_store).visit(parse_webidl(webidl))

    def generate(self):
        return [
            unparse(variable)
            for variable in self._variable_store.vars_as_ast
        ]


def main():
    raw_idl = (Path(__file__).parent / 'idl' / 'std' / 'blob.webidl').resolve()
    idl2js = Idl2Js(str(raw_idl))
    print(idl2js.generate())


if __name__ == '__main__':
    main()
