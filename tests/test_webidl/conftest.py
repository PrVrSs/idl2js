from collections import namedtuple
from pathlib import Path

import pytest


IdlFixtures = namedtuple('IdlFixtures', 'idl baseline')


SYNTAX_FIXTURES = (Path(__file__).parent / 'syntax').resolve()
SYNTAX_IDL_FIXTURES = SYNTAX_FIXTURES / 'idl'
SYNTAX_BASELINE_FIXTURES = SYNTAX_FIXTURES / 'baseline'


@pytest.fixture(params=[
    fixture.name for fixture in SYNTAX_IDL_FIXTURES.glob('*.webidl')
])
def syntax_fixture(request):
    return IdlFixtures(
        idl=SYNTAX_IDL_FIXTURES / request.param,
        baseline=(SYNTAX_BASELINE_FIXTURES / request.param).with_suffix('.json')
    )


INVALID_FIXTURES = (Path(__file__).parent / 'invalid').resolve()
INVALID_IDL_FIXTURES = INVALID_FIXTURES / 'idl'
INVALID_BASELINE_FIXTURES = INVALID_FIXTURES / 'baseline'


@pytest.fixture(params=[
    fixture.name for fixture in INVALID_IDL_FIXTURES.glob('*.webidl')
])
def invalid_fixture(request):
    return IdlFixtures(
        idl=INVALID_IDL_FIXTURES / request.param,
        baseline=(INVALID_BASELINE_FIXTURES / request.param).with_suffix('.json')
    )
