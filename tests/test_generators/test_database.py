import pytest

from idl2js.generators.chooser import ChoiceKind
from idl2js.generators.database import ExampleDatabase


@pytest.fixture
def db(tmp_path):
    return ExampleDatabase(base_path=str(tmp_path / 'test_db'))


class TestExampleDatabase:
    def test_save_and_fetch(self, db):
        choices = [(ChoiceKind.INTEGER, 0, 100, 42)]
        db.save('test_key', choices)

        results = db.fetch('test_key')
        assert len(results) == 1
        assert results[0]['choices'][0][3] == 42

    def test_fetch_empty(self, db):
        assert db.fetch('nonexistent') == []

    def test_save_multiple(self, db):
        c1 = [(ChoiceKind.INTEGER, 0, 100, 10)]
        c2 = [(ChoiceKind.INTEGER, 0, 100, 20)]
        db.save('key', c1)
        db.save('key', c2)

        results = db.fetch('key')
        assert len(results) == 2

    def test_fetch_sorted_by_length(self, db):
        short = [(ChoiceKind.INTEGER, 0, 10, 5)]
        long = [
            (ChoiceKind.INTEGER, 0, 10, 1),
            (ChoiceKind.INTEGER, 0, 10, 2),
            (ChoiceKind.INTEGER, 0, 10, 3),
        ]
        db.save('key', long)
        db.save('key', short)

        results = db.fetch('key')
        assert len(results[0]['choices']) <= len(results[1]['choices'])

    def test_delete(self, db):
        choices = [(ChoiceKind.INTEGER, 0, 100, 42)]
        db.save('key', choices)
        assert len(db.fetch('key')) == 1

        db.delete('key', choices)
        assert len(db.fetch('key')) == 0

    def test_delete_nonexistent(self, db):
        choices = [(ChoiceKind.INTEGER, 0, 100, 42)]
        db.delete('key', choices)

    def test_clear(self, db):
        db.save('k1', [(ChoiceKind.INTEGER, 0, 10, 1)])
        db.save('k2', [(ChoiceKind.INTEGER, 0, 10, 2)])
        db.clear()
        assert db.fetch('k1') == []
        assert db.fetch('k2') == []

    def test_metadata(self, db):
        choices = [(ChoiceKind.INTEGER, 0, 100, 42)]
        db.save('key', choices, metadata={'error': 'TypeError'})

        results = db.fetch('key')
        assert results[0]['metadata']['error'] == 'TypeError'

    def test_keys(self, db):
        db.save('k1', [(ChoiceKind.INTEGER, 0, 10, 1)])
        db.save('k2', [(ChoiceKind.INTEGER, 0, 10, 2)])
        assert len(db.keys()) == 2

    def test_save_returns_path(self, db):
        choices = [(ChoiceKind.INTEGER, 0, 100, 42)]
        path = db.save('key', choices)
        assert path.exists()

    def test_float_choices(self, db):
        choices = [
            (ChoiceKind.FLOAT, 0.0, 1.0, 0.5),
            (ChoiceKind.INTEGER, 0, 10, 5),
        ]
        db.save('key', choices)
        results = db.fetch('key')
        assert len(results[0]['choices']) == 2
