import os
import subprocess
import tempfile
import time

from .browser_runner import wrap_in_html
from .outcome import ExitStatus, Outcome


_CONTAINER_POC_PATH = '/tmp/poc.html'

_DEFAULT_CHROME_ARGS = [
    '--headless',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
]

_DOCKER_ERROR_STRINGS = (
    'docker daemon is not running',
    'cannot connect to the docker daemon',
    'is the docker daemon running',
    'unable to find image',
    'no such image',
    'error response from daemon',
)


def _is_docker_error(returncode, stderr_text):
    if returncode == 125:
        return True
    lower = stderr_text.lower()
    return any(s in lower for s in _DOCKER_ERROR_STRINGS)


def _safe_decode(data):
    if data is None:
        return ''
    if isinstance(data, bytes):
        return data.decode(errors='replace')
    return str(data)


def _classify(result, elapsed):
    stdout = result.stdout.decode(errors='replace')
    stderr = result.stderr.decode(errors='replace')

    if _is_docker_error(result.returncode, stderr):
        return Outcome(
            status=ExitStatus.STARTUP_FAILURE,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_ms=elapsed,
        )

    if result.returncode < 0:
        signal_num = -result.returncode
    elif result.returncode > 128:
        signal_num = result.returncode - 128
    else:
        signal_num = None

    if signal_num is not None:
        return Outcome(
            status=ExitStatus.CRASH,
            exit_code=result.returncode,
            signal=signal_num,
            stdout=stdout,
            stderr=stderr,
            duration_ms=elapsed,
        )

    if result.returncode > 0:
        return Outcome(
            status=ExitStatus.FAILURE,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_ms=elapsed,
        )

    return Outcome(
        status=ExitStatus.SUCCESS,
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        duration_ms=elapsed,
    )


class DockerRunner:
    def __init__(self, image, chrome_path='google-chrome',
                 chrome_args=None, timeout_ms=10000, docker_args=None):
        self._image = image
        self._chrome_path = chrome_path
        self._chrome_args = chrome_args if chrome_args is not None else list(_DEFAULT_CHROME_ARGS)
        self._timeout_s = timeout_ms / 1000.0
        self._docker_args = docker_args or []

    def run(self, js_source):
        html = wrap_in_html(js_source)
        fd, tmp_path = tempfile.mkstemp(prefix='idl2js_', suffix='.html')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)

            cmd = [
                'docker', 'run', '--rm',
                '-v', f'{tmp_path}:{_CONTAINER_POC_PATH}:ro',
                '--entrypoint', self._chrome_path,
                *self._docker_args,
                self._image,
                *self._chrome_args,
                f'file://{_CONTAINER_POC_PATH}',
            ]

            start = time.monotonic()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=self._timeout_s,
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
                    stderr='docker: command not found',
                )

            elapsed = (time.monotonic() - start) * 1000
            return _classify(result, elapsed)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def run_instances(self, instances):
        js_source = '\n'.join(inst.print(save=True) for inst in instances)
        return self.run(js_source)
