from typing import Any, Dict, List

import attr

from .parser import Parser, SyntaxErrorInfo
from .visitor import Visitor


def validate(file: str) -> List[SyntaxErrorInfo]:
    return Parser(file).validate()


def pretty_parse(file: str) -> List[Dict[str, Any]]:
    ast = Visitor(Parser(file).parse()).run()

    return [
        attr.asdict(definition)
        for definition in ast.definitions
    ]
