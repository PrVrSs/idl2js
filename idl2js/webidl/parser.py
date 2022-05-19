from functools import reduce, update_wrapper
from typing import ClassVar, Dict, List, NamedTuple, cast

from antlr4 import BailErrorStrategy, CommonTokenStream, FileStream
from antlr4.error.Errors import ParseCancellationException
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.ErrorStrategy import DefaultErrorStrategy, ErrorStrategy
from antlr4.Parser import ParserRuleContext

from .generated import WebIDLLexer, WebIDLParser
from ..exceptions import IDLParseError


class SyntaxErrorInfo(NamedTuple):

    line: int
    column: int
    message: str

    def __repr__(self):  # pragma: no cover
        return f'{self.line}:{self.column} {self.message}'


class WebIDLErrorListener(ErrorListener):
    def __init__(self):
        self._errors: List[SyntaxErrorInfo] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self._errors.append(SyntaxErrorInfo(line, column, msg))

    @property
    def errors(self) -> List[SyntaxErrorInfo]:
        return self._errors


def _setup_strategy(strategy):
    def decorating_function(parser_function):
        wrapper = _setup_strategy_wrapper(parser_function, strategy)
        return update_wrapper(wrapper, parser_function)

    return decorating_function


def _setup_strategy_wrapper(parser_function, strategy):
    def wrapper(self, *args, **kwargs):
        self.setup_parser_strategy(strategy)
        return parser_function(self, *args, **kwargs)

    return wrapper


class Parser:

    _error_strategies: ClassVar[Dict[str, ErrorStrategy]] = {
        'default': DefaultErrorStrategy(),
        'bail': BailErrorStrategy(),
    }

    def __init__(self, file: str):
        self._parser = self._build_parser(file)
        self._error_listener = self._setup_listener()

    def _setup_listener(self) -> WebIDLErrorListener:
        self._parser.removeErrorListeners()
        self._parser.addErrorListener(error_listener := WebIDLErrorListener())

        return error_listener

    @staticmethod
    def _build_parser(file: str) -> WebIDLParser:
        stream = FileStream(fileName=file, encoding='utf-8')

        functions = (
            WebIDLLexer,
            CommonTokenStream,
            WebIDLParser,
        )

        return cast(
            WebIDLParser,
            reduce(lambda acc, func: func(acc), functions, stream),
        )

    def setup_parser_strategy(self, strategy: str) -> None:
        self._parser._errHandler = self._error_strategies[strategy]

    @_setup_strategy('bail')
    def parse(self) -> ParserRuleContext:
        try:
            return self._parser.webIDL()
        except ParseCancellationException as exc:
            raise IDLParseError from exc

    @_setup_strategy('default')
    def validate(self) -> List[SyntaxErrorInfo]:
        self._parser.webIDL()
        return self._error_listener.errors
