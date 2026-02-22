import random
from enum import IntEnum, auto


class ChoiceKind(IntEnum):
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    INDEX = auto()


class Chooser:
    """Records all random decisions as a replayable choice sequence.

    Inspired by Hypothesis's ConjectureData: every random decision goes
    through this object, producing a linear sequence of choices that can
    be replayed, shrunk, or saved to a database.
    """

    def __init__(self, seed=None):
        self._rng = random.Random(seed)
        self._choices = []
        self._replay = None
        self._replay_index = 0

    def randint(self, a, b):
        if self._replaying:
            value = self._next_replay_value()
            return max(a, min(b, int(value)))

        value = self._rng.randint(a, b)
        self._choices.append((ChoiceKind.INTEGER, a, b, value))
        return value

    def random(self):
        if self._replaying:
            value = self._next_replay_value()
            return max(0.0, min(1.0, value))

        value = self._rng.random()
        self._choices.append((ChoiceKind.FLOAT, 0.0, 1.0, value))
        return value

    def uniform(self, a, b):
        if self._replaying:
            value = self._next_replay_value()
            return max(a, min(b, float(value)))

        value = self._rng.uniform(a, b)
        self._choices.append((ChoiceKind.FLOAT, a, b, value))
        return value

    def choice(self, seq):
        seq = list(seq)
        idx = self.randint(0, len(seq) - 1)
        return seq[idx]

    def shuffle(self, seq):
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]

    @property
    def choices(self):
        return list(self._choices)

    @property
    def _replaying(self):
        return (
            self._replay is not None
            and self._replay_index < len(self._replay)
        )

    def _next_replay_value(self):
        value = self._replay[self._replay_index][3]
        self._replay_index += 1
        return value

    @classmethod
    def from_choices(cls, choices):
        obj = cls()
        obj._replay = list(choices)  # pylint: disable=protected-access
        return obj

    def serialize(self):
        parts = []
        for kind, lo, hi, val in self._choices:
            parts.append(f'{kind}:{lo}:{hi}:{val}')
        return '\n'.join(parts)

    @classmethod
    def deserialize(cls, data):
        choices = []
        for line in data.strip().split('\n'):
            if not line:
                continue
            kind_s, lo_s, hi_s, val_s = line.split(':')
            kind = ChoiceKind(int(kind_s))
            if kind == ChoiceKind.FLOAT:
                choices.append((kind, float(lo_s), float(hi_s), float(val_s)))
            else:
                choices.append((kind, int(lo_s), int(hi_s), int(val_s)))
        return choices
