import attr

from .visitor import Visitor
from .parser import Parser


def validate(file: str):
    return Parser(file).validate()


def pretty_parse(file: str):
    ast = Visitor(Parser(file).parse()).run()

    return [
        attr.asdict(definition)
        for definition in ast.definitions
    ]
