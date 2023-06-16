import random

from ..visitor import NodeTransformer
from .nodes import Ast as JsAst
from .nodes import Literal


class SimpleMutator(NodeTransformer[JsAst]):
    def visit(self, node):
        pass


class LiteralMutator(NodeTransformer[JsAst]):
    def visit_literal(self, _):
        return Literal(value=random.randint(0, 10))


def mutate(ast):
    return LiteralMutator().visit(ast)
