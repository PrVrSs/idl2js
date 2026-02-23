import random
from dataclasses import dataclass, field


@dataclass
class CorpusEntry:
    choices: list
    fingerprint: str
    added_at: int = 0
    age: int = 0
    energy: float = 1.0
    metadata: dict = field(default_factory=dict)


class Corpus:
    def __init__(self, max_size=500, max_age=50, min_size=10):
        self._entries = []
        self._fingerprints = set()
        self._max_size = max_size
        self._max_age = max_age
        self._min_size = min_size
        self._tick = 0

    def add(self, choices, fingerprint, metadata=None):
        if fingerprint in self._fingerprints:
            return None

        entry = CorpusEntry(
            choices=list(choices),
            fingerprint=fingerprint,
            added_at=self._tick,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        self._fingerprints.add(fingerprint)

        if len(self._entries) > self._max_size:
            self._evict()

        return entry

    def select(self):
        if not self._entries:
            return None

        for entry in self._entries:
            entry.energy = 1.0 / (1.0 + entry.age * 0.1)

        weights = [e.energy for e in self._entries]
        total = sum(weights)
        if total == 0:
            chosen = random.choice(self._entries)
        else:
            chosen = random.choices(self._entries, weights=weights, k=1)[0]

        self._tick += 1
        for entry in self._entries:
            entry.age += 1

        return chosen

    def has_fingerprint(self, fp):
        return fp in self._fingerprints

    @property
    def size(self):
        return len(self._entries)

    @property
    def entries(self):
        return list(self._entries)

    def reset(self):
        self._entries.clear()
        self._fingerprints.clear()
        self._tick = 0

    def _evict(self):
        if len(self._entries) <= self._min_size:
            return

        before = list(self._entries)
        self._entries = [
            e for e in self._entries if e.age < self._max_age
        ]

        if len(self._entries) < self._min_size:
            self._entries = before[:self._min_size]

        self._fingerprints = {e.fingerprint for e in self._entries}
