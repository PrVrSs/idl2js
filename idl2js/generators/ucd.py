import json
import sys
from functools import cached_property
from itertools import chain
from pathlib import Path


UCD_DATA = (Path(__file__).parent / 'ucd.json').resolve()


def _read_ucd(ucd_file: str) -> dict[str, list[int]]:
    with open(ucd_file, encoding='utf-8') as fp:
        return json.load(fp)

class UCD:
    """Unicode general categories."""
    def __init__(self, filename: str):
        self.grouped_chars = _read_ucd(ucd_file=filename)

    def query(
        self,
        min_codepoint: int = 0,
        max_codepoint: int = sys.maxunicode,
        exclude_categories: set[str] | None = None,
        include_categories: set[str] | None = None,
        include_characters: set[str] | None = None,
        exclude_characters: set[str] | None = None,
    ):
        categories = self._category_key(
            exclude=exclude_categories or set(),
            include=include_categories or set(),
        )

        all_chars = set(chain.from_iterable(
            self.grouped_chars[category]
            for category in categories
        ))

        char_range = set(filter(lambda char: min_codepoint <= char <= max_codepoint, all_chars))

        include_characters = include_characters and set(map(ord, include_characters)) or set()
        exclude_characters = exclude_characters and set(map(ord, exclude_characters)) or set()

        return sorted(char_range - exclude_characters | include_characters)

    @cached_property
    def _categories(self) -> tuple[str, ...]:
        return tuple(self.grouped_chars.keys())

    def _category_key(
        self,
        exclude: set[str],
        include: set[str],
    ) -> tuple[str, ...]:
        include = include or set(self._categories)

        assert include.issubset(self._categories)
        assert exclude.issubset(self._categories)

        return tuple(include - exclude)


ucd = UCD(filename=str(UCD_DATA))
