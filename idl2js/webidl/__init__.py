from .parser import Parser as WebIDLParser
from .visitor import Visitor as WebIDLVisitor
from .webidl import parse, parse_as_dict, validate


__all__ = (
    'WebIDLParser',
    'WebIDLVisitor',
    'parse',
    'parse_as_dict',
    'validate',
)
