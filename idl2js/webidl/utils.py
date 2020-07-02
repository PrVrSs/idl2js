from collections import deque
from contextlib import suppress
from typing import Optional, TypeVar, Union


_U = TypeVar('_U')


def setup_type(idl_type, type_):
    todo = deque([idl_type])

    with suppress(IndexError):
        while idl_type := todo.popleft():
            idl_type.type = type_

            if idl_type.generic:
                todo.extend(idl_type.idl_type)


def escaped_name(string: Optional[_U]) -> Union[Optional[_U], str]:
    if isinstance(string, str):
        return string.lstrip('_')

    return string
