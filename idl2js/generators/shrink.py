import math

from .chooser import ChoiceKind


class Shrinker:
    """Minimizes a choice sequence while preserving a predicate.

    Args:
        test_function: callable(choices) -> bool, returns True if interesting.
        choices: the initial choice sequence that is known to be interesting.
        max_steps: maximum total shrink attempts before giving up.
    """

    def __init__(self, test_function, choices, max_steps=500):
        self._test = test_function
        self._choices = list(choices)
        self._max_steps = max_steps
        self._steps = 0

    def shrink(self):
        changed = True
        while changed and self._steps < self._max_steps:
            changed = False
            changed |= self._delete_choices()
            changed |= self._zero_choices()
            changed |= self._reduce_integers()
            changed |= self._shrink_floats()
        return self._choices

    def _attempt(self, candidate):
        if self._steps >= self._max_steps:
            return False
        self._steps += 1
        if self._test(candidate):
            self._choices = list(candidate)
            return True
        return False

    def _delete_choices(self):
        changed = False
        for block_size in [8, 4, 2, 1]:
            i = 0
            while i + block_size <= len(self._choices):
                candidate = (
                    self._choices[:i] + self._choices[i + block_size:]
                )
                if self._attempt(candidate):
                    changed = True
                else:
                    i += 1
        return changed

    def _zero_choices(self):
        changed = False
        for i in range(len(self._choices)):  # pylint: disable=consider-using-enumerate
            kind, lo, hi, val = self._choices[i]
            if kind == ChoiceKind.FLOAT:
                zero = max(lo, min(hi, 0.0))
            else:
                zero = max(lo, min(hi, 0))
            if val == zero:
                continue
            candidate = list(self._choices)
            candidate[i] = (kind, lo, hi, zero)
            if self._attempt(candidate):
                changed = True
        return changed

    def _reduce_integers(self):
        changed = False
        for i in range(len(self._choices)):  # pylint: disable=consider-using-enumerate
            kind, lo, hi, val = self._choices[i]
            if kind != ChoiceKind.INTEGER:
                continue

            for target in [lo, 0, 1, -1]:
                target = max(lo, min(hi, target))
                if target == val:
                    continue
                candidate = list(self._choices)
                candidate[i] = (kind, lo, hi, target)
                if self._attempt(candidate):
                    changed = True
                    val = self._choices[i][3]
                    break

            if val == lo:
                continue

            low, high = lo, val
            while low < high:
                mid = (low + high) // 2
                candidate = list(self._choices)
                candidate[i] = (kind, lo, hi, mid)
                if self._attempt(candidate):
                    high = self._choices[i][3]
                else:
                    if mid == low:
                        break
                    low = mid
            if high != val:
                changed = True

        return changed

    def _shrink_floats(self):
        changed = False
        for i in range(len(self._choices)):  # pylint: disable=consider-using-enumerate
            kind, lo, hi, val = self._choices[i]
            if kind != ChoiceKind.FLOAT:
                continue

            if val == 0.0:
                continue

            if math.isinf(val) or math.isnan(val):
                candidate = list(self._choices)
                candidate[i] = (kind, lo, hi, 0.0)
                if self._attempt(candidate):
                    changed = True
                continue

            int_val = int(val)
            if lo <= int_val <= hi:
                candidate = list(self._choices)
                candidate[i] = (kind, lo, hi, float(int_val))
                if self._attempt(candidate):
                    changed = True
                    continue

            half = val / 2
            if lo <= half <= hi:
                candidate = list(self._choices)
                candidate[i] = (kind, lo, hi, half)
                if self._attempt(candidate):
                    changed = True

        return changed

    @property
    def steps(self):
        return self._steps
