import abc
from dataclasses import dataclass, field
from typing import Any, Union


ast_node_map: dict[str, 'Ast'] = {}


@dataclass
class Ast(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        ast_node_map[cls.__name__] = cls


@dataclass
class Program(Ast):
    type: str = field(default='Program')
    source_type: str = field(default='script')
    body: list[Any] = field(default_factory=list)


@dataclass
class Module(Ast):
    type: str = field(default='module')
    source_type: str = field(default='Program')
    body: list[Any] = field(default_factory=list)


@dataclass
class NewExpression(Ast):
    callee: Any
    arguments: list[Any] = field(default_factory=list)
    type: str = field(default='NewExpression')


@dataclass
class VariableDeclaration(Ast):
    type: str = field(default='VariableDeclaration')
    kind: str = field(default='let')
    declarations: list[Any] = field(default_factory=list)


@dataclass
class VariableDeclarator(Ast):
    id: str
    init: Any
    type: str = field(default='VariableDeclarator')


@dataclass
class Identifier(Ast):
    name: str
    type: str = field(default='Identifier')


@dataclass
class MemberExpression(Ast):
    object: Any
    property: Any
    computed: bool = field(default=False)
    type: str = field(default='MemberExpression')


@dataclass
class CallExpression(Ast):
    callee: Any
    arguments: list[Any] = field(default_factory=list)
    type: str = field(default='CallExpression')


@dataclass
class Literal(Ast):
    raw: Any = field(init=False)
    value: Any
    type: str = field(default='Literal')

    def __post_init__(self):
        if isinstance(self.value, bool):
            self.raw = 'true' if self.value is True else 'false'
        elif isinstance(self.value, int):
            self.raw = str(self.value)
        elif isinstance(self.value, str):
            self.raw = f"'{self.value}'"
        else:
            self.raw = self.value


@dataclass
class BlockStatement(Ast):
    body: list[Any] = field(default_factory=list)
    type: str = field(default='BlockStatement')


@dataclass
class CatchClause(Ast):
    param: Identifier = field()
    block: BlockStatement = field()
    type: str = field(default='CatchClause')


@dataclass
class TryStatement(Ast):
    handler: Any
    block: BlockStatement = field()
    finalizer: Any | None = field(default=None)
    type: str = field(default='TryStatement')


@dataclass
class AssignmentExpression(Ast):
    left: Identifier
    right: Any
    operator: str = field(default='=')
    type: str = field(default='AssignmentExpression')


@dataclass
class ExpressionStatement(Ast):
    expression: Any = field()
    type: str = field(default='ExpressionStatement')


@dataclass
class ArrayExpression(Ast):
    type: str = field(default='ArrayExpression')
    elements: list[Any] = field(default_factory=list)


@dataclass
class Property(Ast):
    key: Any = field()
    value: Any = field()
    type: str = field(default='Property')
    method: bool = field(default=False)
    shorthand: bool = field(default=False)
    computed: bool = field(default=False)


@dataclass
class ObjectExpression(Ast):
    type: str = field(default='ObjectExpression')
    properties: list[Property] = field(default_factory=list)


Expression = Union[
    AssignmentExpression,
    NewExpression,
    MemberExpression,
    CallExpression,
    ObjectExpression,
    ArrayExpression,
]
