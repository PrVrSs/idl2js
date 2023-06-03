import sys

from more_itertools import first

from .ucd import ucd
from .vose_sampler import VoseSampler


class Generator:

    def generate(self):
        raise NotImplementedError(f'{type(self).__name__}.generate')


class CharGenerator(Generator):
    """A generator which generates single char."""
    def __init__(
        self,
        min_codepoint: int = 0,
        max_codepoint: int = sys.maxunicode,
        exclude_categories: set[str] | None = None,
        include_categories: set[str] | None = None,
        include_characters: set[str] | None = None,
        exclude_characters: set[str] | None = None,
    ):
        self._chars = ucd.query(
            min_codepoint=min_codepoint,
            max_codepoint=max_codepoint,
            include_categories=include_categories,
            exclude_categories=exclude_categories,
            include_characters=include_characters,
            exclude_characters=exclude_characters,
        )

    def generate(self) -> str:
        return chr(first(VoseSampler(data=self._chars).sample(size=1)))


class InterfaceGenerator(Generator):
    def __init__(self, generator_opt):
        self._opt = generator_opt


class ArrayGenerator(Generator):
    def __init__(self, elements, min_size=0, max_size=float('inf')):
        self.min_size = min_size
        self.max_size = max_size
        self.elements = elements

    def generate(self):
        return []
