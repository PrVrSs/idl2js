import os
import shutil
import subprocess
import tempfile
import time

from .outcome import ExitStatus, Outcome


_CHROME_NAMES = (
    'google-chrome',
    'google-chrome-stable',
    'chromium',
    'chromium-browser',
    'chrome',
)

_DEFAULT_ARGS = [
    '--headless',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
]

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
{js_source}
window.close();
</script>
</body>
</html>"""


def _find_chrome():
    for name in _CHROME_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _safe_decode(data):
    if data is None:
        return ''
    if isinstance(data, bytes):
        return data.decode(errors='replace')
    return str(data)


def wrap_in_html(js_source):
    return _HTML_TEMPLATE.format(js_source=js_source)


class BrowserRunner:
    def __init__(self, chrome_path=None, chrome_args=None,
                 timeout_ms=10000, env=None):
        self._chrome = chrome_path or _find_chrome()
        self._chrome_args = chrome_args if chrome_args is not None else list(_DEFAULT_ARGS)
        self._timeout_s = timeout_ms / 1000.0
        self._env = env

    def run(self, js_source):
        if not self._chrome:
            return Outcome(
                status=ExitStatus.STARTUP_FAILURE,
                exit_code=-1,
                stderr='Chrome not found',
            )

        html = wrap_in_html(js_source)
        fd, tmp_path = tempfile.mkstemp(prefix='idl2js_', suffix='.html')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)

            cmd = [self._chrome, *self._chrome_args, f'file://{tmp_path}']

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
                    stderr=f'Engine not found: {self._chrome}',
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
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def run_instances(self, instances):
        js_source = '\n'.join(inst.print(save=True) for inst in instances)
        return self.run(js_source)
