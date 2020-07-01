from typing import Any, List

import attr


class AST:
    ...


@attr.s
class Module(AST):

    type: str = attr.ib(default='module')
    source_type: str = attr.ib(default='Program')
    body: List[Any] = attr.ib(factory=list)


@attr.s
class NewExpression(AST):

    callee = attr.ib()
    arguments = attr.ib(factory=list)
    type = attr.ib(default='NewExpression')


@attr.s
class VariableDeclaration(AST):

    type: str = attr.ib(default='VariableDeclaration')
    kind: str = attr.ib(default='let')
    declarations: List[Any] = attr.ib(factory=list)


@attr.s
class VariableDeclarator(AST):

    id = attr.ib()
    init = attr.ib()
    type: str = attr.ib(default='VariableDeclarator')


@attr.s
class Identifier(AST):

    name: str = attr.ib()
    type: str = attr.ib(default='Identifier')


@attr.s
class MemberExpression(AST):

    object = attr.ib()
    property = attr.ib()
    computed: bool = attr.ib(default=False)
    type: str = attr.ib(default='MemberExpression')


@attr.s
class CallExpression(AST):

    callee = attr.ib()
    arguments = attr.ib(factory=list)
    type: str = attr.ib(default='CallExpression')


@attr.s
class AssignmentExpression(AST):
    ...


@attr.s
class ArrayExpression(AST):
    ...


@attr.s
class ObjectExpression(AST):
    ...


@attr.s
class Literal(AST):
    ...


@attr.s
class Property(AST):
    ...
