import random
import time


class _RNGProxy:
    """Proxy that delegates to a swappable backing RNG.

    All modules import this single object. When the backing RNG is
    swapped (e.g. to a Chooser for recording), all callers see the
    new implementation immediately.
    """

    def __init__(self):
        self._backing = random.Random(time.process_time())

    def seed(self, value):
        self._backing.seed(value)

    def randint(self, a, b):
        return self._backing.randint(a, b)

    def random(self):
        return self._backing.random()

    def uniform(self, a, b):
        return self._backing.uniform(a, b)

    def choice(self, seq):
        return self._backing.choice(seq)

    def shuffle(self, seq):
        return self._backing.shuffle(seq)

    def install(self, backing):
        self._backing = backing

    def reset(self):
        self._backing = random.Random(time.process_time())


idl2js_random = _RNGProxy()
