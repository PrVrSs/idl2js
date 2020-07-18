from typing import Any, Dict, List

import attr

from .nodes import Ast
from .parser import Parser, SyntaxErrorInfo
from .visitor import Visitor


def validate(file: str) -> List[SyntaxErrorInfo]:
    return Parser(file).validate()


def parse(file: str) -> Ast:
    return Visitor(Parser(file).parse()).run()


def parse_as_dict(file: str) -> Dict[str, Any]:
    return attr.asdict(parse(file))
