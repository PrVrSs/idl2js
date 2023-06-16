from typing import Any

from .const import CATCH_CONSTANT, LET
from .nodes import (
    ArrayExpression,
    AssignmentExpression,
    BlockStatement,
    CallExpression,
    CatchClause,
    Expression,
    ExpressionStatement,
    Identifier,
    Literal,
    MemberExpression,
    NewExpression,
    ObjectExpression,
    Property,
    TryStatement,
    VariableDeclaration,
    VariableDeclarator,
)


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


def create_dict(name, properties) -> ExpressionStatement:
    return create_expression(
        name=name,
        expression=ObjectExpression(
            properties=properties,
        ),
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


def create_array(elements: list[Any]) -> ArrayExpression:
    return ArrayExpression(elements=elements)


def try_statement(var: VariableDeclaration) -> TryStatement:
    return TryStatement(
        block=BlockStatement(body=[var]),
        handler=CatchClause(
            param=Identifier(name=CATCH_CONSTANT),
            block=BlockStatement(body=[]),
        ),
    )


def create_literal(value: Any) -> Literal:
    return Literal(value=value)


def create_identifier(name: str) -> Identifier:
    return Identifier(name=name)


def create_property(key: Any, value: Any) -> Property:
    return Property(key=key, value=value)
