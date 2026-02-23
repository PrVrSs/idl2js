import pytest

from idl2js.engine import EngineConfig, EngineStats


class TestEngineConfig:
    def test_defaults(self):
        cfg = EngineConfig(idl_type='Foo', idls=('a.webidl',))
        assert cfg.engine == 'node'
        assert cfg.timeout_ms == 5000
        assert cfg.seed_count == 20
        assert cfg.max_iterations == 1000
        assert cfg.max_consecutive_mutations == 5
        assert cfg.mutation_rate == 0.1
        assert cfg.corpus_max_size == 500
        assert cfg.db_path is None

    def test_custom_values(self):
        cfg = EngineConfig(
            idl_type='Bar',
            idls=('b.webidl',),
            engine='d8',
            timeout_ms=2000,
            seed_count=10,
            max_iterations=500,
            db_path='/tmp/test_db',
        )
        assert cfg.engine == 'd8'
        assert cfg.timeout_ms == 2000
        assert cfg.seed_count == 10
        assert cfg.db_path == '/tmp/test_db'


class TestEngineStats:
    def test_defaults(self):
        s = EngineStats()
        assert s.executions == 0
        assert s.crashes == 0
        assert s.exec_per_s == 0.0
        assert s.chain_success_rate == 0.0

    def test_chain_success_rate(self):
        s = EngineStats(chain_attempts=10, chain_successes=3)
        assert s.chain_success_rate == pytest.approx(0.3)

    def test_exec_per_s_zero_elapsed(self):
        s = EngineStats(executions=100)
        assert s.exec_per_s == 0.0
