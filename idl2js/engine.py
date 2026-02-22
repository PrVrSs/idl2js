import logging
import time
from dataclasses import dataclass, field

from .corpus import Corpus
from .execution.outcome import ExitStatus
from .execution.runner import Runner
from .fuzzer import Fuzzer
from .generators.database import ExampleDatabase
from .generators.mutator import mutate_choices


log = logging.getLogger(__name__)


@dataclass
class EngineConfig:  # pylint: disable=too-many-instance-attributes
    idl_type: str
    idls: tuple[str, ...]
    engine: str = 'node'
    engine_args: list[str] = field(default_factory=list)
    timeout_ms: int = 5000
    seed_count: int = 20
    max_iterations: int = 1000
    max_consecutive_mutations: int = 5
    mutation_rate: float = 0.1
    corpus_max_size: int = 500
    corpus_max_age: int = 50
    corpus_min_size: int = 10
    db_path: str | None = None
    options: dict | None = None


@dataclass
class EngineStats:  # pylint: disable=too-many-instance-attributes
    executions: int = 0
    crashes: int = 0
    timeouts: int = 0
    failures: int = 0
    successes: int = 0
    corpus_size: int = 0
    unique_fingerprints: int = 0
    chain_attempts: int = 0
    chain_successes: int = 0
    start_time: float = 0.0

    @property
    def elapsed_s(self):
        if self.start_time == 0.0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def exec_per_s(self):
        elapsed = self.elapsed_s
        if elapsed == 0.0:
            return 0.0
        return self.executions / elapsed

    @property
    def chain_success_rate(self):
        if self.chain_attempts == 0:
            return 0.0
        return self.chain_successes / self.chain_attempts


class FuzzEngine:  # pylint: disable=too-many-instance-attributes
    def __init__(self, config):
        self._config = config
        self._fuzzer = Fuzzer(idls=config.idls)
        self._runner = Runner(
            engine=config.engine,
            engine_args=config.engine_args,
            timeout_ms=config.timeout_ms,
        )
        self._corpus = Corpus(
            max_size=config.corpus_max_size,
            max_age=config.corpus_max_age,
            min_size=config.corpus_min_size,
        )
        self._db = ExampleDatabase(config.db_path) if config.db_path else None
        self._stats = EngineStats()
        self._on_crash = []
        self._on_interesting = []
        self._on_stats = []

    @property
    def stats(self):
        self._stats.corpus_size = self._corpus.size
        return self._stats

    @property
    def corpus(self):
        return self._corpus

    def on_crash(self, callback):
        self._on_crash.append(callback)

    def on_interesting(self, callback):
        self._on_interesting.append(callback)

    def on_stats(self, callback):
        self._on_stats.append(callback)

    def run(self):
        self._stats.start_time = time.monotonic()

        for _ in range(self._config.seed_count):
            self._generate_and_evaluate()

        remaining = self._config.max_iterations - self._config.seed_count
        for _ in range(max(0, remaining)):
            parent = self._corpus.select()
            if parent is None:
                self._generate_and_evaluate()
            else:
                self._consecutive_mutate(parent.choices)

        self._fire_stats()

    def _generate_and_evaluate(self):
        try:
            sample, choices = self._fuzzer.generate_one_recorded(
                self._config.idl_type, self._config.options,
            )
        except Exception:  # pylint: disable=broad-except
            return

        outcome = self._runner.run_instances(sample)
        self._record_execution(outcome)
        self._evaluate(outcome, choices, sample)

    def _consecutive_mutate(self, parent_choices):
        current_choices = parent_choices

        for _ in range(self._config.max_consecutive_mutations):
            mutated = mutate_choices(
                current_choices,
                mutation_rate=self._config.mutation_rate,
            )

            try:
                sample = self._fuzzer.replay(
                    self._config.idl_type, mutated, self._config.options,
                )
            except Exception:  # pylint: disable=broad-except
                break

            outcome = self._runner.run_instances(sample)
            self._record_execution(outcome)
            self._evaluate(outcome, mutated, sample)

            self._stats.chain_attempts += 1

            if outcome.is_crash or outcome.is_timeout:
                break
            if outcome.is_success:
                self._stats.chain_successes += 1
                current_choices = mutated
            else:
                break

    def _evaluate(self, outcome, choices, sample):
        fp = outcome.fingerprint()

        if outcome.is_crash:
            self._corpus.add(choices, fp, metadata={'type': 'crash'})
            self._persist(choices, fp, 'crash')
            for cb in self._on_crash:
                cb(outcome, choices, sample)
            for cb in self._on_interesting:
                cb(outcome, choices, sample)
            return

        if outcome.is_timeout and not self._corpus.has_fingerprint('timeout'):
            self._corpus.add(choices, fp, metadata={'type': 'timeout'})
            self._persist(choices, fp, 'timeout')
            for cb in self._on_interesting:
                cb(outcome, choices, sample)
            return

        if outcome.status == ExitStatus.FAILURE:
            if not self._corpus.has_fingerprint(fp):
                self._corpus.add(choices, fp, metadata={'type': 'failure'})
                self._persist(choices, fp, 'failure')
                for cb in self._on_interesting:
                    cb(outcome, choices, sample)
            return

        if outcome.is_success and not self._corpus.has_fingerprint(fp):
            self._corpus.add(choices, fp, metadata={'type': 'success'})

    def _record_execution(self, outcome):
        self._stats.executions += 1

        if outcome.is_crash:
            self._stats.crashes += 1
        elif outcome.is_timeout:
            self._stats.timeouts += 1
        elif outcome.status == ExitStatus.FAILURE:
            self._stats.failures += 1
        elif outcome.is_success:
            self._stats.successes += 1

        self._stats.unique_fingerprints = self._corpus.size

    def _persist(self, choices, fingerprint, kind):
        if self._db is None:
            return
        key = f'{self._config.idl_type}:{kind}'
        self._db.save(key, choices, metadata={'fingerprint': fingerprint})

    def _fire_stats(self):
        self._stats.corpus_size = self._corpus.size
        for cb in self._on_stats:
            cb(self._stats)
