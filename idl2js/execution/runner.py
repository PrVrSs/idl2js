import subprocess
import time

from .outcome import ExitStatus, Outcome


class Runner:
    def __init__(self, engine='node', engine_args=None, timeout_ms=5000, env=None):
        self._engine = engine
        self._engine_args = engine_args or []
        self._timeout_s = timeout_ms / 1000.0
        self._env = env

    def run(self, js_source):
        cmd = [self._engine, *self._engine_args, '-e', js_source]

        start = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self._timeout_s,
                env=self._env,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = (time.monotonic() - start) * 1000
            return Outcome(
                status=ExitStatus.TIMEOUT,
                exit_code=-1,
                stdout=_safe_decode(exc.stdout),
                stderr=_safe_decode(exc.stderr),
                duration_ms=elapsed,
            )
        except FileNotFoundError:
            return Outcome(
                status=ExitStatus.STARTUP_FAILURE,
                exit_code=-1,
                stderr=f'Engine not found: {self._engine}',
            )

        elapsed = (time.monotonic() - start) * 1000

        if result.returncode < 0:
            return Outcome(
                status=ExitStatus.CRASH,
                exit_code=result.returncode,
                signal=-result.returncode,
                stdout=result.stdout.decode(errors='replace'),
                stderr=result.stderr.decode(errors='replace'),
                duration_ms=elapsed,
            )

        if result.returncode != 0:
            return Outcome(
                status=ExitStatus.FAILURE,
                exit_code=result.returncode,
                stdout=result.stdout.decode(errors='replace'),
                stderr=result.stderr.decode(errors='replace'),
                duration_ms=elapsed,
            )

        return Outcome(
            status=ExitStatus.SUCCESS,
            exit_code=0,
            stdout=result.stdout.decode(errors='replace'),
            stderr=result.stderr.decode(errors='replace'),
            duration_ms=elapsed,
        )

    def run_instances(self, instances):
        js_source = '\n'.join(inst.print(save=True) for inst in instances)
        return self.run(js_source)


def _safe_decode(data):
    if data is None:
        return ''
    if isinstance(data, bytes):
        return data.decode(errors='replace')
    return str(data)
