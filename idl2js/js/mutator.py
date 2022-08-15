import random

from .nodes import Ast as JsAst, Literal
from ..visitor import NodeTransformer


class SimpleMutator(NodeTransformer[JsAst]):
    def visit(self):
        pass


class LiteralMutator(NodeTransformer[JsAst]):
    def visit_literal(self, node):
        return Literal(value=random.randint(0, 10))


def mutate(ast):
    return LiteralMutator().visit(ast)
