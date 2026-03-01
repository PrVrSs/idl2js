import sys
from functools import partial

from more_itertools import first

from .coin import biased_coin
from .rng import idl2js_random
from .strategy import (
    FLOAT_SPECIAL_VALUES,
    GenerationStrategy,
    float_boundary_values,
    integer_boundary_values,
    select_strategy,
)
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
        self._sampler = VoseSampler(data=self._chars)

    def generate(self) -> str:
        return chr(first(self._sampler.sample(size=1)))


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
    def __init__(
        self,
        min_value: int | None = None,
        max_value: int | None = None,
        strategy: GenerationStrategy | None = None,
    ):
        self._min_value = min_value
        self._max_value = max_value
        self._strategy = strategy
        self._boundaries = None

    def _get_boundaries(self):
        if self._boundaries is None:
            self._boundaries = integer_boundary_values(
                self._min_value, self._max_value,
            )
        return self._boundaries

    def generate(self):
        strategy = self._strategy or select_strategy()

        if strategy == GenerationStrategy.BOUNDARY:
            boundaries = self._get_boundaries()
            if boundaries:
                return idl2js_random.choice(boundaries)

        if strategy == GenerationStrategy.SPECIAL:
            special = [0, 1, -1]
            valid = [
                v for v in special
                if self._min_value <= v <= self._max_value
            ]
            if valid:
                return idl2js_random.choice(valid)

        return idl2js_random.randint(self._min_value, self._max_value)


class ArrayGenerator(Generator):
    def __init__(
        self,
        element_generator,
        min_size: int = 2,
        max_size: int = 10,
        strategy: GenerationStrategy | None = None,
    ):
        self.min_size = min_size
        self.max_size = max_size
        self.element_generator = element_generator
        self._strategy = strategy

    def generate(self):
        strategy = self._strategy or select_strategy()

        if strategy == GenerationStrategy.BOUNDARY:
            size = idl2js_random.choice([0, 1, self.max_size])
            return [
                self.element_generator.generate() for _ in range(size)
            ]

        if strategy == GenerationStrategy.SPECIAL:
            size = idl2js_random.choice([
                0, self.max_size, self.max_size + 5,
            ])
            return [
                self.element_generator.generate() for _ in range(size)
            ]

        return [
            self.element_generator.generate()
            for _ in many(self.min_size, self.max_size)
        ]


class ChoiceGenerator(Generator):
    def __init__(self, elements, coverage=None):
        self.elements = elements
        self._sampler = VoseSampler(data=self.elements)
        self._coverage = coverage
        self._chosen = set()

    def generate(self):
        if self._coverage:
            uncovered = [
                e for e in set(self.elements) if e not in self._chosen
            ]
            if uncovered:
                choice = idl2js_random.choice(uncovered)
                self._chosen.add(choice)
                return choice

        result = first(self._sampler.sample(size=1))
        self._chosen.add(result)
        return result


class TextGenerator(ArrayGenerator):
    def generate(self):
        strategy = self._strategy or select_strategy()

        if strategy == GenerationStrategy.SPECIAL:
            return idl2js_random.choice([
                '',
                '\x00',
                '\n',
                ' ' * 50,
                'a' * 100,
            ])

        if strategy == GenerationStrategy.BOUNDARY:
            size = idl2js_random.choice([0, 1, self.max_size])
            if size == 0:
                return ''
            return ''.join(
                self.element_generator.generate() for _ in range(size)
            )

        return ''.join(
            self.element_generator.generate()
            for _ in many(self.min_size, self.max_size)
        )


class BooleanGenerator(Generator):
    def generate(self):
        return idl2js_random.choice([True, False])


class FloatGenerator(Generator):
    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 1.0,
        unrestricted: bool = False,
        strategy: GenerationStrategy | None = None,
    ):
        self._min_value = min_value
        self._max_value = max_value
        self._unrestricted = unrestricted
        self._strategy = strategy
        self._boundaries = None

    def _get_boundaries(self):
        if self._boundaries is None:
            self._boundaries = float_boundary_values(
                self._min_value, self._max_value,
            )
        return self._boundaries

    def generate(self):
        strategy = self._strategy or select_strategy()

        if strategy == GenerationStrategy.SPECIAL and self._unrestricted:
            return idl2js_random.choice(FLOAT_SPECIAL_VALUES)

        if strategy == GenerationStrategy.BOUNDARY:
            boundaries = self._get_boundaries()
            if boundaries:
                return idl2js_random.choice(boundaries)

        if strategy == GenerationStrategy.SPECIAL:
            return idl2js_random.choice([0.0, -0.0, 1.0, -1.0])

        return idl2js_random.uniform(self._min_value, self._max_value)


class UndefinedGenerator(Generator):
    def generate(self):
        return None


class AnyGenerator(Generator):
    def generate(self):
        gen = idl2js_random.choice([
            BooleanGenerator(),
            IntegerGenerator(min_value=-2**31, max_value=2**31 - 1),
            FloatGenerator(),
        ])
        return gen.generate()


class SymbolGenerator(Generator):
    def generate(self):
        return f'Symbol("{idl2js_random.randint(0, 9999)}")'


class ObjectGenerator(Generator):
    def generate(self):
        return {}


class BigIntGenerator(Generator):
    def __init__(
        self,
        strategy: GenerationStrategy | None = None,
    ):
        self._strategy = strategy
        self._min = -2**63
        self._max = 2**63 - 1

    def generate(self):
        strategy = self._strategy or select_strategy()

        if strategy == GenerationStrategy.BOUNDARY:
            boundaries = integer_boundary_values(self._min, self._max)
            if boundaries:
                return idl2js_random.choice(boundaries)

        if strategy == GenerationStrategy.SPECIAL:
            return idl2js_random.choice([0, 1, -1])

        return idl2js_random.randint(self._min, self._max)


def integer(_, options):
    return partial(
        IntegerGenerator,
        min_value=options.get('min_value'),
        max_value=options.get('max_value'),
    )


def text(_, options):
    return partial(TextGenerator, element_generator=CharGenerator(
        min_codepoint=options.get('min_codepoint', 0),
        max_codepoint=options.get('max_codepoint', sys.maxunicode),
        exclude_categories=options.get('exclude_categories'),
        include_categories=options.get('include_categories'),
        include_characters=options.get('include_characters'),
        exclude_characters=options.get('exclude_characters'),
    ))


def boolean(_, _options):
    return BooleanGenerator


def float_(_, options):
    return partial(
        FloatGenerator,
        min_value=options.get('min_value'),
        max_value=options.get('max_value'),
        unrestricted=options.get('unrestricted', False),
    )


def undefined(_, _options):
    return UndefinedGenerator


def any_type(_, _options):
    return AnyGenerator


def symbol(_, _options):
    return SymbolGenerator


def object_type(_, _options):
    return ObjectGenerator


def bigint(_, _options):
    return partial(
        BigIntGenerator,
    )
