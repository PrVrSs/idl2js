import uuid

from .const import LET
from .nodes import VariableDeclaration, VariableDeclarator, Identifier


def unique_name_generator():
    return f'v_{uuid.uuid4().hex}'


class VariableStorage:

    variables = {}

    def __init__(self):
        self._interface = ''

    @property
    def interface(self):
        return self._interface

    def create_variable(self, expression, interface=False):
        unique_name = unique_name_generator()

        self.variables[unique_name] = VariableDeclaration(
            kind=LET,
            declarations=[
                VariableDeclarator(
                    id=Identifier(name=unique_name),
                    init=expression,
                )
            ],
        )

        if interface is True:
            self._interface = unique_name


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
