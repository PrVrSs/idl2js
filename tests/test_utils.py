from idl2js.utils import is_hashable

import pytest


@pytest.mark.parametrize('test_input, expected', [
    (1, True),
    ('', True),
    ((), True),
    ([], False),
    ({}, False),
    (set(), False),
])
def test_is_hashable(test_input, expected):
    assert is_hashable(test_input) is expected
