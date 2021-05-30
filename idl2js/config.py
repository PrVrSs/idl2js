import os
from collections.abc import Mapping
from typing import Any, Iterator


class Block(Mapping):

    def __init__(self, /, **kwargs: Any):
        self._data = kwargs

    def __getitem__(self, item: str) -> str:
        return self._data[item]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class Config:

    def __init__(self):
        self._env = os.environ.copy()
        self._config = {}

    def _setup_parser(self):
        self._config['PARSER'] = Block(
            **self._parser_defaults(),
        )

    @staticmethod
    def _parser_defaults():
        return Block(
            num_of_process=4,
        )
