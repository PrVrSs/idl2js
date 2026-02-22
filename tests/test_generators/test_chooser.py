import pytest

from idl2js.generators.chooser import Chooser, ChoiceKind


class TestChooser:
    def test_randint_records(self):
        c = Chooser(seed=42)
        val = c.randint(0, 100)
        assert 0 <= val <= 100
        assert len(c.choices) == 1
        assert c.choices[0][0] == ChoiceKind.INTEGER

    def test_random_records(self):
        c = Chooser(seed=42)
        val = c.random()
        assert 0.0 <= val <= 1.0
        assert len(c.choices) == 1
        assert c.choices[0][0] == ChoiceKind.FLOAT

    def test_uniform_records(self):
        c = Chooser(seed=42)
        val = c.uniform(-5.0, 5.0)
        assert -5.0 <= val <= 5.0
        assert len(c.choices) == 1

    def test_choice_records(self):
        c = Chooser(seed=42)
        val = c.choice(['a', 'b', 'c'])
        assert val in ['a', 'b', 'c']
        assert len(c.choices) == 1

    def test_deterministic_with_seed(self):
        c1 = Chooser(seed=42)
        c2 = Chooser(seed=42)
        assert c1.randint(0, 1000) == c2.randint(0, 1000)
        assert c1.random() == c2.random()
        assert c1.uniform(-1, 1) == c2.uniform(-1, 1)

    def test_different_seeds_differ(self):
        c1 = Chooser(seed=42)
        c2 = Chooser(seed=99)
        results1 = [c1.randint(0, 10000) for _ in range(10)]
        results2 = [c2.randint(0, 10000) for _ in range(10)]
        assert results1 != results2

    def test_multiple_choices_recorded(self):
        c = Chooser(seed=42)
        c.randint(0, 10)
        c.random()
        c.uniform(1.0, 2.0)
        c.randint(5, 15)
        assert len(c.choices) == 4


class TestChooserReplay:
    def test_replay_integers(self):
        c1 = Chooser(seed=42)
        vals = [c1.randint(0, 100) for _ in range(5)]

        c2 = Chooser.from_choices(c1.choices)
        replayed = [c2.randint(0, 100) for _ in range(5)]
        assert vals == replayed

    def test_replay_mixed(self):
        c1 = Chooser(seed=42)
        v1 = c1.randint(0, 100)
        v2 = c1.random()
        v3 = c1.uniform(-1.0, 1.0)

        c2 = Chooser.from_choices(c1.choices)
        assert c2.randint(0, 100) == v1
        assert c2.random() == v2
        assert c2.uniform(-1.0, 1.0) == v3

    def test_replay_clamps_to_range(self):
        choices = [(ChoiceKind.INTEGER, 0, 100, 50)]
        c = Chooser.from_choices(choices)
        assert c.randint(60, 80) == 60


class TestChooserSerialization:
    def test_serialize_deserialize(self):
        c = Chooser(seed=42)
        c.randint(0, 100)
        c.random()
        c.uniform(-5.0, 5.0)

        serialized = c.serialize()
        deserialized = Chooser.deserialize(serialized)

        assert len(deserialized) == 3
        for orig, deser in zip(c.choices, deserialized):
            assert orig[0] == deser[0]
            assert orig[3] == pytest.approx(deser[3])

    def test_roundtrip_replay(self):
        c1 = Chooser(seed=42)
        vals = [c1.randint(0, 100) for _ in range(3)]

        serialized = c1.serialize()
        loaded = Chooser.deserialize(serialized)
        c2 = Chooser.from_choices(loaded)

        replayed = [c2.randint(0, 100) for _ in range(3)]
        assert vals == replayed


class TestChooserShuffle:
    def test_shuffle_records(self):
        c = Chooser(seed=42)
        items = [1, 2, 3, 4, 5]
        c.shuffle(items)
        assert sorted(items) == [1, 2, 3, 4, 5]
        assert len(c.choices) > 0
