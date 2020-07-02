from pathlib import Path

from idl2js.webidl import WebIDLParser, WebIDLVisitor
from idl2js.webidl.nodes import Ast as WebIDLAst

from idl2js.js.nodes import (
    CallExpression,
    Identifier,
    MemberExpression,
    NewExpression,
)
from idl2js.storages import VariableStorage, DefinitionStorage
from idl2js.visitor import Visitor, T


class InterfaceTransformer(Visitor[T]):

    def __init__(self, variable_storage: VariableStorage):
        self._variable_storage = variable_storage

    def visit_interface(self, node) -> None:
        if node.partial is True:
            return

        self._variable_storage.create_variable(
            NewExpression(
                callee=Identifier(name=node.name),
                arguments=[],
            ))

        self.generic_visit(node)

    def visit_attribute(self, node):
        self._variable_storage.create_variable(
            MemberExpression(
                object=Identifier(name=self._variable_storage.interface),
                property=Identifier(name=node.name),
            ),
            idl_type=node.idl_type
        )

        self.generic_visit(node)

    def visit_operation(self, node):
        self._variable_storage.create_variable(
            CallExpression(
                callee=MemberExpression(
                    object=Identifier(name=self._variable_storage.interface),
                    property=Identifier(name=node.name)
                ),
                arguments=[]
            ),
            idl_type=node.idl_type
        )

        self.generic_visit(node)


class ConversionRule:
    pass


class CollectTypedef(Visitor[T]):

    def __init__(self, definition_storage):
        self._definition_storage = definition_storage

    def visit_typedef(self, node):
        self._definition_storage.add_typedef(
            node.name, self.visit(node.idl_type))

    def visit_idl_type(self, node):
        idl_type = node.idl_type

        if idl_type is None:
            return

        if isinstance(idl_type, str):
            return idl_type

        if isinstance(idl_type, list):
            return [self.visit(idl) for idl in idl_type]

        return self.visit(idl_type)


class DefinitionCollector(Visitor[T]):

    def __init__(self, definition_storage: DefinitionStorage):
        self._definition_storage = definition_storage

    def visit_interface(self, node) -> None:
        self._definition_storage.interfaces[node.name] = node

    def visit_typedef(self, node) -> None:
        self._definition_storage.typedefs[node.name] = node

    def visit_dictionary(self, node) -> None:
        self._definition_storage.dictionaries[node.name] = node

    def visit_enum(self, node) -> None:
        self._definition_storage.enums[node.name] = node


def main():
    raw_idl = (Path(__file__).parent / 'interfaces' / 'blob.webidl').resolve()

    idl_ast = WebIDLVisitor(WebIDLParser(str(raw_idl)).parse()).run()

    var_store = VariableStorage()
    # td = DefinitionCollector(storage).visit(idl_ast)

    InterfaceTransformer[WebIDLAst](variable_storage=var_store).visit(idl_ast)
    print(var_store.vars_as_ast)


if __name__ == '__main__':
    main()
