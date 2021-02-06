import uuid

from typing import NamedTuple, Union

from idl2js.storage import Storage
from idl2js.built_in_types import BuiltInTypes
from idl2js.js.const import LET
from idl2js.js.nodes import (
    Ast,
    CallExpression,
    Identifier,
    Literal,
    NewExpression,
    MemberExpression,
    VariableDeclaration,
    VariableDeclarator,
)


Expression = Union[NewExpression, MemberExpression, CallExpression]


class Variable(NamedTuple):
    type: str
    ast: Ast


def unique_name_generator():
    return f'v_{uuid.uuid4().hex}'


def variable_ast(name: str, expression: Expression) -> VariableDeclaration:
    return VariableDeclaration(
        kind=LET,
        declarations=[
            VariableDeclarator(id=Identifier(name=name), init=expression),
        ]
    )


def create_object(name, progenitor, arguments) -> VariableDeclaration:
    return variable_ast(
        name=name,
        expression=NewExpression(
            callee=Identifier(name=progenitor),
            arguments=arguments,
        )
    )


def create_attribute(name, progenitor, method) -> VariableDeclaration:
    return variable_ast(
        name=name,
        expression=MemberExpression(
            object=Identifier(name=progenitor),
            property=Identifier(name=method),
        )
    )


def create_operation(name, progenitor, method, arguments) -> VariableDeclaration:
    return variable_ast(
        name=name,
        expression=CallExpression(
            arguments=arguments,
            callee=MemberExpression(
                object=Identifier(name=progenitor),
                property=Identifier(name=method),
            ),
        )
    )


def create_variable(type_: str, ast: Ast) -> Variable:
    return Variable(type=type_, ast=ast)


class Builder:
    def __init__(self, storage: Storage, std_types: BuiltInTypes):
        self._storage = storage
        self._std_types = std_types

    def create_arguments(self, arguments):
        return [
            Literal(value=self._std_types.generate(argument.idl_type.idl_type))
            for argument in arguments
        ]
