import pytest

from idl2js.generators.ucd import ucd


@pytest.mark.parametrize('test_input, expected', [
    (dict(min_codepoint=0, max_codepoint=128), list(range(0, 129))),
    (dict(min_codepoint=0, max_codepoint=128, include_categories={'Lu'}), list(range(65, 91))),
    (
            dict(min_codepoint=0, max_codepoint=128, include_categories={'Lu'}, include_characters={'♞'}),
            [*list(range(65, 91)), 9822]
    ),
])
def test_ucd_query(test_input, expected):
    assert ucd.query(**test_input) == expected
