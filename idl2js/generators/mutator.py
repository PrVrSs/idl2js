import math

from .rng import idl2js_random


def mutate_integer(value, min_value=None, max_value=None):
    mutations = [
        _int_add_small,
        _int_flip_bit,
        _int_negate,
        _int_to_boundary,
    ]

    mutator = idl2js_random.choice(mutations)
    result = mutator(value, min_value, max_value)

    if min_value is not None:
        result = max(result, min_value)
    if max_value is not None:
        result = min(result, max_value)

    return result


def mutate_float(value, min_value=None, max_value=None):
    mutations = [
        _float_add_small,
        _float_multiply,
        _float_negate,
        _float_special,
    ]

    mutator = idl2js_random.choice(mutations)
    result = mutator(value, min_value, max_value)

    if result is not None and not math.isnan(result) and not math.isinf(result):
        if min_value is not None:
            result = max(result, min_value)
        if max_value is not None:
            result = min(result, max_value)

    return result


def mutate_string(value):
    if not value:
        return idl2js_random.choice(['', 'a', '\x00', '\n'])

    mutations = [
        _str_insert_char,
        _str_delete_char,
        _str_replace_char,
        _str_duplicate,
        _str_reverse,
    ]

    return idl2js_random.choice(mutations)(value)


def mutate_array(value, element_mutator=None):
    if not value:
        return value

    mutations = [
        _arr_shuffle,
        _arr_duplicate_element,
        _arr_remove_element,
        _arr_reverse,
    ]

    mutator = idl2js_random.choice(mutations)
    result = mutator(list(value))

    if element_mutator and result:
        idx = idl2js_random.randint(0, len(result) - 1)
        result[idx] = element_mutator(result[idx])

    return result


def _int_add_small(value, _min, _max):
    delta = idl2js_random.choice([-1, 1, -2, 2, -10, 10])
    return value + delta


def _int_flip_bit(value, _min, _max):
    bit = idl2js_random.randint(0, 63)
    return value ^ (1 << bit)


def _int_negate(value, _min, _max):
    return -value


def _int_to_boundary(_value, min_value, max_value):
    candidates = [0, 1, -1]
    if min_value is not None:
        candidates.extend([min_value, min_value + 1])
    if max_value is not None:
        candidates.extend([max_value, max_value - 1])
    return idl2js_random.choice(candidates)


def _float_add_small(value, _min, _max):
    delta = idl2js_random.uniform(-1.0, 1.0)
    return value + delta


def _float_multiply(value, _min, _max):
    factor = idl2js_random.choice([0.5, 2.0, -1.0, 0.1, 10.0])
    return value * factor


def _float_negate(value, _min, _max):
    return -value


def _float_special(_value, _min, _max):  # pylint: disable=unused-argument
    return idl2js_random.choice([0.0, -0.0, math.nan, math.inf, -math.inf])


def _str_insert_char(value):
    pos = idl2js_random.randint(0, len(value))
    char = chr(idl2js_random.randint(0, 127))
    return value[:pos] + char + value[pos:]


def _str_delete_char(value):
    if not value:
        return value
    pos = idl2js_random.randint(0, len(value) - 1)
    return value[:pos] + value[pos + 1:]


def _str_replace_char(value):
    if not value:
        return value
    pos = idl2js_random.randint(0, len(value) - 1)
    char = chr(idl2js_random.randint(0, 127))
    return value[:pos] + char + value[pos + 1:]


def _str_duplicate(value):
    return value + value


def _str_reverse(value):
    return value[::-1]


def _arr_shuffle(value):
    result = list(value)
    idl2js_random.shuffle(result)
    return result


def _arr_duplicate_element(value):
    if not value:
        return value
    idx = idl2js_random.randint(0, len(value) - 1)
    return value[:idx] + [value[idx]] + value[idx:]


def _arr_remove_element(value):
    if not value:
        return value
    idx = idl2js_random.randint(0, len(value) - 1)
    return value[:idx] + value[idx + 1:]


def _arr_reverse(value):
    return list(reversed(value))
