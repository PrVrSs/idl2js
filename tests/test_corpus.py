from idl2js.corpus import Corpus, CorpusEntry


class TestCorpusAdd:
    def test_novel_entry(self):
        c = Corpus()
        entry = c.add([(1, 0, 10, 5)], 'crash:signal:11')
        assert entry is not None
        assert entry.fingerprint == 'crash:signal:11'
        assert c.size == 1

    def test_duplicate_rejected(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'crash:signal:11')
        dup = c.add([(1, 0, 10, 7)], 'crash:signal:11')
        assert dup is None
        assert c.size == 1

    def test_different_fingerprints(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'crash:signal:11')
        c.add([(1, 0, 10, 7)], 'crash:signal:6')
        assert c.size == 2

    def test_metadata(self):
        c = Corpus()
        entry = c.add([(1, 0, 10, 5)], 'fp1', metadata={'kind': 'crash'})
        assert entry.metadata == {'kind': 'crash'}


class TestCorpusSelect:
    def test_empty_corpus(self):
        c = Corpus()
        assert c.select() is None

    def test_returns_entry(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'fp1')
        entry = c.select()
        assert entry is not None
        assert isinstance(entry, CorpusEntry)

    def test_ages_entries(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'fp1')
        c.select()
        assert c.entries[0].age == 1
        c.select()
        assert c.entries[0].age == 2

    def test_energy_decay(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'fp1')
        entry = c.select()
        initial_energy = entry.energy
        c.select()
        assert c.entries[0].energy < initial_energy


class TestCorpusEviction:
    def test_evicts_over_max(self):
        c = Corpus(max_size=5, max_age=2, min_size=2)
        for i in range(5):
            c.add([(1, 0, 10, i)], f'fp{i}')

        # Age all entries past max_age
        for _ in range(3):
            c.select()

        # Adding one more should trigger eviction
        c.add([(1, 0, 10, 99)], 'fp_new')
        assert c.size <= 5

    def test_respects_min_size(self):
        c = Corpus(max_size=5, max_age=1, min_size=3)
        for i in range(5):
            c.add([(1, 0, 10, i)], f'fp{i}')

        # Age past max
        for _ in range(5):
            c.select()

        # Force eviction
        c.add([(1, 0, 10, 99)], 'fp_new')
        assert c.size >= 3


class TestCorpusReset:
    def test_reset(self):
        c = Corpus()
        c.add([(1, 0, 10, 5)], 'fp1')
        c.add([(1, 0, 10, 7)], 'fp2')
        assert c.size == 2
        c.reset()
        assert c.size == 0
        assert not c.has_fingerprint('fp1')

    def test_has_fingerprint(self):
        c = Corpus()
        assert not c.has_fingerprint('fp1')
        c.add([(1, 0, 10, 5)], 'fp1')
        assert c.has_fingerprint('fp1')
