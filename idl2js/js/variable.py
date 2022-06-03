from typing import NamedTuple

from .nodes import Ast


class Variable(NamedTuple):
    type: str
    ast: Ast


def create_js_variable(type_: str, ast: Ast) -> Variable:
    return Variable(type=type_, ast=ast)
