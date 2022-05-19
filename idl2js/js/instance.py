from .nodes import ExpressionStatement
from .statements import try_statement
from .unparser import unparse


class Instance:
    def __init__(self, type_: str, ast: ExpressionStatement):
        self._type = type_
        self._ast = ast

        self._spawn: list[Instance] = []

    def __repr__(self):
        return self.print(save=True)

    @property
    def name(self) -> str:
        return self._ast.expression.left.name

    def print(self, save: bool = True) -> str:
        return unparse(try_statement(self._ast) if save else self._ast)
