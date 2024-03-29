import sys
from functools import partial

from more_itertools import first

from .coin import biased_coin
from .rng import idl2js_random
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


class many:  # pylint: disable=invalid-name
    def __init__(self, min_size, max_size):
        self.min_size = min_size
        self.max_size = max_size
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.min_size > self.count:
            should_continue = True
        elif self.min_size == self.max_size:
            should_continue = self.count < self.min_size
        else:
            should_continue = biased_coin()

        if should_continue is False or self.max_size <= self.count:
            raise StopIteration

        self.count += 1

        return self.count


class IntegerGenerator(Generator):
    def __init__(self, min_value: int | None = None, max_value: int | None = None):
        self._min_value = min_value
        self._max_value = max_value

    def generate(self):
        return idl2js_random.randint(self._min_value, self._max_value)


class ArrayGenerator(Generator):
    def __init__(self, element_generator, min_size: int = 2, max_size: int = 10):
        self.min_size = min_size
        self.max_size = max_size

        self.element_generator = element_generator

    def generate(self):
        return [
            self.element_generator.generate()
            for _ in many(self.min_size, self.max_size)
        ]


class ChoiceGenerator(Generator):
    def __init__(self, elements):
        self.elements = elements
    def generate(self):
        return first(VoseSampler(data=self.elements).sample(size=1))

class TextGenerator(ArrayGenerator):
    def generate(self):
        return ''.join(super().generate())


class BooleanGenerator(Generator):
    def generate(self):
        return idl2js_random.choice([True, False])

def integer(_, options):
    return partial(
        IntegerGenerator,
        min_value=options.get('min_value'),
        max_value=options.get('max_value'),
    )


def text(_, options):
    return partial(TextGenerator, element_generator=CharGenerator(**options))
