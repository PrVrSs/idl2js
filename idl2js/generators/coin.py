from idl2js.generators.rng import idl2js_random


def _flip_coin(p: float) -> bool:
    return idl2js_random.uniform(0, 1) <= p


def _factor(n: int) -> int:
    if n == 0:
        return 0

    s = 0
    while n % 2 == 0:
        s +=  1
        n /=  2

    return s


def biased_coin(p: float = 0.5) -> bool:
    k = 0
    m = 0
    while True:
        k += 1

        toss = _flip_coin(p)
        if toss is False:
            if _factor(k) - _factor(k - m) > 0:
                return False
            continue

        m += 1
        if _factor(k) - _factor(m) > 0:
            return True
