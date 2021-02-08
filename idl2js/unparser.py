from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterator, NewType

from idl2js.converter import InterfaceTransformer
from idl2js.js.nodes import Ast as JsAst
from idl2js.storage import Storage
from idl2js.visitor import AstType, Visitor
from idl2js.webidl import parse
from idl2js.webidl.nodes import Ast as WebIDLAst
from idl2js.utils import interleave


Parenthesis = NewType('Parenthesis', str)

PAREN = Parenthesis('paren')
BRACE = Parenthesis('brace')
BRACKET = Parenthesis('bracket')

_parentheses: Dict[Parenthesis, SimpleNamespace] = {
    PAREN: SimpleNamespace(open='(', close=')'),
    BRACE: SimpleNamespace(open='{', close='}'),
    BRACKET: SimpleNamespace(open='[', close=']'),
}


class Unparser(Visitor[AstType]):
    """
    Methods in this class recursively traverse an AST and output source code
    for the abstract syntax.
    """
    def __init__(self):
        self._source = []

    def write(self, text):
        self._source.append(text)

    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            super().visit(node)

    def visit(self, node) -> str:
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

    def visit_call_expression(self, node):
        self.traverse(node.callee)

        with self._parentheses(PAREN):
            interleave(
                iterable=node.arguments,
                func=self.traverse,
                separator=lambda: self.write(', ')
            )

    def visit_literal(self, node):
        self.write(node.raw)

    def visit_try_statement(self, node):
        self.write('try ')

        with self._parentheses(BRACE):
            self.traverse(node.block)

        self.traverse(node.handler)

    def visit_catch_clause(self, node):
        self.write(' catch')

        with self._parentheses(PAREN):
            self.traverse(node.param)

        with self._parentheses(BRACE):
            self.traverse(node.block)

    def visit_block_statement(self, node):
        interleave(
            iterable=node.body,
            func=self.traverse,
            separator=lambda: self.write('\n')
        )

    def visit_assignment_expression(self, node):
        self.traverse(node.left)

        self.write(' = ')

        self.traverse(node.right)

    @contextmanager
    def _parentheses(self, paren: Parenthesis) -> Iterator[None]:
        self.write(_parentheses[paren].open)
        yield
        self.write(_parentheses[paren].close)


def unparse(ast: JsAst) -> str:
    return Unparser[JsAst]().visit(ast)


def main():
    from idl2js.builder import Builder, try_statement
    from idl2js.built_in_types import BuiltInTypes

    raw_idl = (Path(__file__).parent.parent / 'blob.webidl').resolve()
    idl_ast = parse(str(raw_idl))

    var_store = Storage()

    InterfaceTransformer[WebIDLAst](
        storage=var_store,
        builder=Builder(storage=var_store, std_types=BuiltInTypes())
    ).visit(idl_ast)

    for variable in var_store._var:
        print(unparse(try_statement(variable.ast)))


if __name__ == '__main__':
    main()
