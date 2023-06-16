from .nodes import ExpressionStatement
from .statements import try_statement
from .unparser import unparse


class Instance:
    def __init__(self, idl_type: str, ast: ExpressionStatement):
        self._idl_type = idl_type
        self._ast = ast

    def __repr__(self):
        return self.print(save=True)

    @property
    def idl_type(self):
        return self._idl_type

    @property
    def name(self) -> str:
        return self._ast.expression.left.name

    def print(self, save: bool = True) -> str:
        return unparse(try_statement(self._ast) if save else self._ast)
