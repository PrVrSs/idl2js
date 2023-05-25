from decimal import Decimal
from typing import Generic, TypeVar

from idl2js.generators.rng import idl2js_random


T = TypeVar('T')


def proportions(items: T) -> dict[T, Decimal]:
    increment = Decimal(1) / len(items)

    return {
        item: increment
        for item in items
    }


class VoseSampler(Generic[T]):
    """http://www.keithschwarz.com/darts-dice-coins/"""
    def __init__(self, data: list[T]):
        self.data = proportions(data)

        self._table_prob = {}
        self._table_alias = {}

        self._alias_initialisation()

    def sample(self, size: int = 1) -> list[T]:
        """ Return a sample of size n from the distribution."""
        return [
            self._alias_generation()
            for _ in range(size)
        ]

    @property
    def _table_prob_list(self):
        return list(self._table_prob)

    def _alias_initialisation(self):
        small = []
        large = []

        n = len(self.data)
        for item, probability in self.data.items():
            self._table_prob[item] = Decimal(probability) * n

            if self._table_prob[item] < 1:
                small.append(item)
            else:
                large.append(item)

        while small and large:
            s = small.pop()
            l = large.pop()

            self._table_alias[s] = l
            self._table_prob[l] = (self._table_prob[l] + self._table_prob[s]) - Decimal(1)

            if self._table_prob[l] < 1:
                small.append(l)
            else:
                large.append(l)

        while large:
            self._table_prob[large.pop()] = Decimal(1)

        while small:
            self._table_prob[small.pop()] = Decimal(1)

    def _alias_generation(self):
        item = idl2js_random.choice(self._table_prob_list)

        if self._table_prob[item] >= idl2js_random.random():
            return item

        return self._table_alias[item]
