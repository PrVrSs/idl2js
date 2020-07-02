import uuid
from typing import NamedTuple

from idl2js.js.const import LET
from idl2js.js.nodes import VariableDeclaration, VariableDeclarator, Identifier


def unique_name_generator():
    return f'v_{uuid.uuid4().hex}'


class Variable(NamedTuple):
    # возможно стоит построить граф: какие переменные из каких получились.
    # и такую структуру использовать в `VariableStorage`.
    name: str
    type: str


class VariableStorage:
    """
    сделать crud.
    отделить `vars` `vars_as_ast`
    """
    vars = []
    vars_as_ast = []

    def __init__(self):
        self._interface = ''

    @property
    def interface(self):
        return self._interface

    def create_variable(self, expression, idl_type=None):
        unique_name = unique_name_generator()

        self.vars_as_ast.append(
            VariableDeclaration(
                kind=LET,
                declarations=[
                    VariableDeclarator(
                        id=Identifier(name=unique_name),
                        init=expression,
                    )
                ],
            )
        )

        if idl_type is None:
            self._interface = unique_name
            var_type = expression.callee.name
        else:
            var_type = idl_type.idl_type

        self.vars.append(Variable(name=unique_name, type=var_type))


class DefinitionStorage:
    """
    нужна линеаризация зависимостей
    сделать 1 словарь
    """

    def __init__(self):
        self._typedefs = dict()
        self._interfaces = dict()
        self._dictionaries = dict()
        self._enums = dict()

    @property
    def typedefs(self):
        return self._typedefs

    @property
    def interfaces(self):
        return self._interfaces

    @property
    def dictionaries(self):
        return self._dictionaries

    @property
    def enums(self):
        return self._enums
