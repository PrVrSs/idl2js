import json

from idl2js.webidl import validate


def test_invalid(invalid_fixture):
    with invalid_fixture.baseline.open() as expected:
        assert [
            error._asdict() for error in validate(invalid_fixture.idl)
        ] == json.load(expected)
