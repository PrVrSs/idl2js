import json

from idl2js.webidl import pretty_parse


def test_syntax(syntax_fixture):
    with syntax_fixture.baseline.open() as expected:
        assert pretty_parse(syntax_fixture.idl) == json.load(expected)
