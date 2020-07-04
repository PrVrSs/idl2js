from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import NewType, Dict

from idl2js.converter import InterfaceTransformer
from idl2js.js.nodes import Ast as JsAst
from idl2js.storages import VariableStorage
from idl2js.visitor import Visitor, T
from idl2js.webidl import WebIDLParser, WebIDLVisitor
from idl2js.webidl.nodes import Ast as WebIDLAst


Parenthesis = NewType('Parenthesis', str)

PAREN = Parenthesis('paren')
BRACE = Parenthesis('brace')
BRACKET = Parenthesis('bracket')

_parentheses: Dict[Parenthesis, SimpleNamespace] = {
    PAREN: SimpleNamespace(open='(', close=')'),
    BRACE: SimpleNamespace(open='{', close='}'),
    BRACKET: SimpleNamespace(open='[', close=']'),
}


def interleave(iterable, func, separator):
    it = iter(iterable)

    try:
        func(next(it))
    except StopIteration:
        pass
    else:
        for x in it:
            separator()
            func(x)


class Unparser(Visitor[T]):
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

    @contextmanager
    def _parentheses(self, paren: Parenthesis) -> None:
        self.write(_parentheses[paren].open)
        yield
        self.write(_parentheses[paren].close)


def unparse(ast: JsAst) -> str:
    return Unparser[JsAst]().visit(ast)


def _dump_js(variables, file='tmp.json'):
    # tmp
    import attr
    import json

    with open(file, 'w') as f:
        json.dump(
            obj=[attr.asdict(variable) for variable in variables],
            fp=f,
            indent=4,
        )


def main():
    raw_idl = (Path(__file__).parent / 'idl' / 'blob.webidl').resolve()
    idl_ast = WebIDLVisitor(WebIDLParser(str(raw_idl)).parse()).run()

    var_store = VariableStorage()

    InterfaceTransformer[WebIDLAst](variable_storage=var_store).visit(idl_ast)

    for variable in var_store.vars_as_ast:
        print(unparse(variable))


if __name__ == '__main__':
    main()
