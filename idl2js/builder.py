import uuid

from typing import NamedTuple

from idl2js.storage import Storage
from idl2js.built_in_types import BuiltInTypes
from idl2js.js.const import LET
from idl2js.js.nodes import (
    AssignmentExpression,
    Ast,
    BlockStatement,
    Expression,
    ExpressionStatement,
    CallExpression,
    CatchClause,
    Identifier,
    Literal,
    NewExpression,
    MemberExpression,
    TryStatement,
    VariableDeclaration,
    VariableDeclarator,
)


CATCH_CONSTANT: str = 'e'


class Variable(NamedTuple):
    type: str
    ast: Ast


def unique_name():
    return f'v_{uuid.uuid4().hex}'


def variable_ast(name: str, expression: Expression) -> VariableDeclaration:
    return VariableDeclaration(
        kind=LET,
        declarations=[
            VariableDeclarator(id=Identifier(name=name), init=expression),
        ]
    )


def create_expression(name: str, expression: Expression) -> ExpressionStatement:
    return ExpressionStatement(
            expression=AssignmentExpression(
                left=Identifier(name=name),
                right=expression,
            )
    )


def create_object(name, progenitor, arguments) -> ExpressionStatement:
    return create_expression(
        name=name,
        expression=NewExpression(
            callee=Identifier(name=progenitor),
            arguments=arguments,
        )
    )


def create_attribute(name, progenitor, method) -> ExpressionStatement:
    return create_expression(
        name=name,
        expression=MemberExpression(
            object=Identifier(name=progenitor),
            property=Identifier(name=method),
        )
    )


def create_operation(name, progenitor, method, arguments) -> ExpressionStatement:
    return create_expression(
        name=name,
        expression=CallExpression(
            arguments=arguments,
            callee=MemberExpression(
                object=Identifier(name=progenitor),
                property=Identifier(name=method),
            ),
        )
    )


def try_statement(var: VariableDeclaration) -> TryStatement:
    return TryStatement(
        block=BlockStatement(body=[var]),
        handler=CatchClause(
            param=Identifier(name=CATCH_CONSTANT),
            block=BlockStatement(body=[]),
        ),
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
