import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Iterator, NamedTuple, Optional

from pywebidl2 import parse, validate
from pywebidl2.exceptions import IDLParseError
from pywebidl2.expr import Ast
from more_itertools import partition


logger = logging.getLogger(__name__)


class ParseResult(NamedTuple):
    item: Optional[Ast] = None
    error: Optional[str] = None


def parse_idl(file: str) -> ParseResult:
    try:
        return ParseResult(item=parse(file))
    except IDLParseError:
        return ParseResult(
            error='Skipped {file}\n{errors}'.format(  # pylint: disable=consider-using-f-string
                file=file,
                errors='\n'.join(map(str, validate(file))),
            )
        )
    except Exception as exc:
        return ParseResult(error=str(exc))


class IDLProcessor:
    def __init__(self, idl_files: tuple[str, ...], process: int = 4):
        self._idl_files = idl_files
        self._process = process

    def _parse(self) -> Iterator[ParseResult]:
        with ProcessPoolExecutor(self._process) as pool:
            yield from pool.map(parse_idl, self._idl_files)

    def parse(self) -> list[Ast]:
        successes, fails = partition(
            pred=lambda result: result.item is None, iterable=self._parse())

        for fail in fails:
            logger.debug(fail.error)

        return [success.item for success in successes]  # type: ignore


def process_idl(idl_files: tuple[str, ...]) -> list[Ast]:
    return IDLProcessor(idl_files).parse()
