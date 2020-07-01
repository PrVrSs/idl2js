from pathlib import Path
from types import SimpleNamespace
from collections import deque

from pywebidl2 import Idl, antlr_visitor

from idl2js.visitor import Visitor
from idl2js.converter import InterfaceTransformer
from idl2js.storages import VariableStorage


PAREN = 'paren'
BRACE = 'brace'
BRACKET = 'bracket'


class parentheses:

    _parentheses = {
        PAREN: SimpleNamespace(open='(', close=')'),
        BRACE: SimpleNamespace(open='{', close='}'),
        BRACKET: SimpleNamespace(open='[', close=']'),
    }

    def __init__(self, unparser):
        self._unparser = unparser

        self._queue = deque()

    def __call__(self, paren_type):
        self._queue.append(parent := self._parentheses[paren_type])
        self._unparser.write(parent.open)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._unparser.write(self._queue.pop().close)

    __enter__ = lambda self: ...


class Unparser(Visitor):

    def __init__(self):
        self._source = []
        self._parentheses = parentheses(self)

    def write(self, text):
        self._source.append(text)

    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            super().visit(node)

    def visit(self, node):
        self._source = []
        self.traverse(node)

        return ''.join(self._source)

    def visit_identifier(self, node):
        self.write(node.name)

    def visit_variable_declaration(self, node):
        self.write(f'{node.kind} ')

        self.traverse(node.declarations)

    def visit_variable_declarator(self, node):
        self.traverse(node.id)

        self.write(' = ')

        self.traverse(node.init)

    def visit_new_expression(self, node):
        self.write('new ')
        self.traverse(node.callee)

        with self._parentheses(PAREN):
            self.traverse(node.arguments)

    def visit_member_expression(self, node):
        self.traverse(node.object)

        self.write('.')

        self.traverse(node.property)


def unparse(ast):
    return Unparser().visit(ast)


def main():
    raw_idl = (Path(__file__).parent / 'webidls' / 'blob.webidl').resolve()
    idl_ast = antlr_visitor.Visitor(Idl(str(raw_idl)).parse()).run()
    var_store = VariableStorage()

    InterfaceTransformer(variable_storage=var_store).visit(idl_ast)
    print(var_store.vars)
    for variable in var_store.vars_as_ast:
        print(unparse(variable))


if __name__ == '__main__':
    main()
