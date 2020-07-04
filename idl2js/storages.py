import string
import uuid
from random import choice, randint
from typing import NamedTuple

from idl2js.js.const import LET
from idl2js.js.nodes import (
    Identifier,
    Literal,
    VariableDeclaration,
    VariableDeclarator,
)


def unique_name_generator():
    return f'v_{uuid.uuid4().hex}'


class Variable(NamedTuple):
    # возможно стоит построить граф: какие переменные из каких получились.
    # и такую структуру использовать в `VariableStorage`.
    name: str
    type: str


i32 = (-2**31, 2**31 - 1)


class StdTypes:
    """
    добавить, чтобы через конфиг задать какой-нибудь тип
    и его возможные значения
    мб также сделать возможным: задавать аргументы методов определенных объектов
    как определенные значения так и рандомный диапозон

    Blob:
        slice:
        - 0..=100
        - random
        - String:
            ...

    подумать над форматом, как содержимого так и самого конфига yaml, ini, etc.
    """
    def find_type(self, type_):
        if type_ == 'long long':
            return self.long_long()
        elif type_ == 'DOMString':
            return self.dom_string()

        return type_

    def long_long(self):
        return randint(*i32)

    def dom_string(self):
        return ''.join(
            choice(string.ascii_lowercase)
            for _ in range(randint(1, 10))
        )


class VariableStorage:
    """
    сделать crud.
    отделить `vars` `vars_as_ast`
    """
    vars = []
    vars_as_ast = []

    def __init__(self):
        self._interface = ''
        self._std_types = StdTypes()

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

    def create_arguments(self, arguments):
        return [
            self.create_variable_by_idl_type(argument.idl_type)
            for argument in arguments
        ]

    def create_variable_by_idl_type(self, node):
        return Literal(value=self._std_types.find_type(node.idl_type))


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
