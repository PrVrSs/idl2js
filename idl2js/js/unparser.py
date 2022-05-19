from contextlib import contextmanager
from types import SimpleNamespace
from typing import Dict, Iterator, NewType

from .nodes import Ast as JsAst
from ..visitor import Visitor
from ..utils import interleave


Parenthesis = NewType('Parenthesis', str)

PAREN = Parenthesis('paren')
BRACE = Parenthesis('brace')
BRACKET = Parenthesis('bracket')

_parentheses: Dict[Parenthesis, SimpleNamespace] = {
    PAREN: SimpleNamespace(open='(', close=')'),
    BRACE: SimpleNamespace(open='{', close='}'),
    BRACKET: SimpleNamespace(open='[', close=']'),
}


class Unparser(Visitor[JsAst]):
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
            interleave(
                iterable=node.arguments,
                func=self.traverse,
                separator=lambda: self.write(', ')
            )

    def visit_object_expression(self, node):
        with self._parentheses(BRACE):
            interleave(
                iterable=node.properties,
                func=self.traverse,
                separator=lambda: self.write(', ')
            )

    def visit_property(self, node):
        self.write(node.key)

        self.write(': ')

        self.traverse(node.value)

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

    def visit_array_expression(self, node):
        with self._parentheses(BRACKET):
            interleave(
                iterable=node.elements,
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
    return Unparser().visit(ast)
