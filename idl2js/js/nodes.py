import abc
from typing import Any, List, Optional, Union

import attr


@attr.s
class Ast(abc.ABC):
    ...


@attr.s
class Module(Ast):

    type: str = attr.ib(default='module')
    source_type: str = attr.ib(default='Program')
    body: List[Any] = attr.ib(factory=list)


@attr.s
class NewExpression(Ast):

    callee = attr.ib()
    arguments = attr.ib(factory=list)
    type = attr.ib(default='NewExpression')


@attr.s
class VariableDeclaration(Ast):

    type: str = attr.ib(default='VariableDeclaration')
    kind: str = attr.ib(default='let')
    declarations: List[Any] = attr.ib(factory=list)


@attr.s
class VariableDeclarator(Ast):

    id = attr.ib()
    init = attr.ib()
    type: str = attr.ib(default='VariableDeclarator')


@attr.s
class Identifier(Ast):

    name: str = attr.ib()
    type: str = attr.ib(default='Identifier')


@attr.s
class MemberExpression(Ast):

    object = attr.ib()
    property = attr.ib()
    computed: bool = attr.ib(default=False)
    type: str = attr.ib(default='MemberExpression')


@attr.s
class CallExpression(Ast):

    callee = attr.ib()
    arguments = attr.ib(factory=list)
    type: str = attr.ib(default='CallExpression')


@attr.s
class Literal(Ast):

    raw = attr.ib(init=False)
    value = attr.ib()
    type: str = attr.ib(default='Literal')

    def __attrs_post_init__(self):
        if isinstance(self.value, int):
            self.raw = str(self.value)
        elif isinstance(self.value, str):
            self.raw = f"'{self.value}'"
        else:
            self.raw = self.value


@attr.s
class BlockStatement(Ast):

    body: List[Any] = attr.ib(factory=list)
    type: str = attr.ib(default='BlockStatement')


@attr.s
class CatchClause:
    param: Identifier = attr.ib()
    block: BlockStatement = attr.ib()
    type: str = attr.ib(default='CatchClause')


@attr.s
class TryStatement(Ast):

    handler = attr.ib()
    block: BlockStatement = attr.ib()
    finalizer: Optional[Any] = attr.ib(default=None)
    type: str = attr.ib(default='TryStatement')


@attr.s
class AssignmentExpression(Ast):

    left: Identifier = attr.ib()
    right: Any = attr.ib()
    operator: str = attr.ib(default='=')
    type: str = attr.ib(default='AssignmentExpression')


@attr.s
class ExpressionStatement(Ast):

    expression: Any = attr.ib()
    type: str = attr.ib(default='ExpressionStatement')


@attr.s
class ArrayExpression(Ast):
    ...


@attr.s
class Property(Ast):

    key: Any = attr.ib()
    value: Any = attr.ib()
    type: str = attr.ib(default='Property')
    method: bool = attr.ib(default=False)
    shorthand: bool = attr.ib(default=False)
    computed: bool = attr.ib(default=False)


@attr.s
class ObjectExpression(Ast):

    type: str = attr.ib(default='ObjectExpression')
    properties: List[Property] = attr.ib(factory=list)


Expression = Union[
    AssignmentExpression,
    NewExpression,
    MemberExpression,
    CallExpression,
    ObjectExpression,
]
