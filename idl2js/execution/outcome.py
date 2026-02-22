import re
from dataclasses import dataclass
from enum import IntEnum, auto


class ExitStatus(IntEnum):
    SUCCESS = auto()
    FAILURE = auto()
    CRASH = auto()
    TIMEOUT = auto()
    STARTUP_FAILURE = auto()


@dataclass(frozen=True)
class Outcome:
    status: ExitStatus
    exit_code: int
    signal: int | None = None
    stdout: str = ''
    stderr: str = ''
    duration_ms: float = 0.0

    @property
    def is_crash(self):
        return self.status == ExitStatus.CRASH

    @property
    def is_timeout(self):
        return self.status == ExitStatus.TIMEOUT

    @property
    def is_success(self):
        return self.status == ExitStatus.SUCCESS

    @property
    def error_pattern(self):
        if not self.stderr:
            return ''
        first_line = self.stderr.strip().split('\n', maxsplit=1)[0]
        normalized = re.sub(r'"[^"]*"', '"..."', first_line)
        normalized = re.sub(r"'[^']*'", "'...'", normalized)
        normalized = re.sub(r'0x[0-9a-fA-F]+', '0x...', normalized)
        normalized = re.sub(r'\b\d+(\.\d+)?\b', 'N', normalized)
        return normalized

    def fingerprint(self):
        if self.is_crash:
            return f'crash:signal:{self.signal}'
        if self.is_timeout:
            return 'timeout'
        if self.status == ExitStatus.FAILURE:
            return f'failure:{self.error_pattern}'
        return 'success'
