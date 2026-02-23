import re
from pathlib import Path

from idl2js.fuzzer import Fuzzer


EXAMPLES_DIR = Path(__file__).parent
IDL_FILE = str(EXAMPLES_DIR / 'cve_targets.webidl')
UINT32_MAX = 0xFFFFFFFF
MAX_SAMPLES = 100


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
    dict_pattern = re.compile(
        r'try \{(v_\w+) = \{(.+?)\}\} catch',
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

        m = dict_pattern.search(text)
        if m:
            var_name, props_str = m.groups()
            props = {}
            for prop in props_str.split(','):
                prop = prop.strip()
                if ':' in prop:
                    key, val_ref = prop.split(':', 1)
                    val_ref = val_ref.strip()
                    if val_ref in variables:
                        props[key.strip()] = variables[val_ref]
                    else:
                        props[key.strip()] = val_ref
            variables[var_name] = props
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


# ---------------------------------------------------------------------------
# Vulnerability oracles
# ---------------------------------------------------------------------------

def check_integer_overflow(sample):
    """CVE-2017-5112: check if ImageData(sw, sh) has sw * sh * 4 > UINT32_MAX."""
    _, constructors = parse_js_output(sample)
    for type_name, args in constructors:
        if type_name == 'ImageData' and len(args) == 2:
            w = _parse_number(args[0])
            h = _parse_number(args[1])
            if w is not None and h is not None and w > 0 and h > 0:
                if w * h * 4 > UINT32_MAX:
                    return True, (w, h)
    return False, None


def check_special_float(sample):
    """CVE-2023-1222: check if OscillatorNode options contain inf/nan."""
    _, constructors = parse_js_output(sample)
    for type_name, args in constructors:
        if type_name == 'OscillatorNode':
            for arg in args:
                if isinstance(arg, dict):
                    for key in ('frequency', 'detune'):
                        val = arg.get(key, '')
                        if isinstance(val, str):
                            low = val.lower()
                            if 'inf' in low or 'nan' in low:
                                return True, (key, val)
    return False, None


def check_zero_dimension(sample):
    """CVE-2016-1935: check if ImageData has a zero width or height."""
    _, constructors = parse_js_output(sample)
    for type_name, args in constructors:
        if type_name == 'ImageData' and len(args) == 2:
            w = _parse_number(args[0])
            h = _parse_number(args[1])
            if w is not None and h is not None:
                if w == 0 or h == 0:
                    return True, (w, h)
    return False, None


# ---------------------------------------------------------------------------
# Hunt functions
# ---------------------------------------------------------------------------

def hunt_cve(fuzzer, idl_type, oracle, cve_id, description):
    """Run the fuzzer and search for a CVE pattern.

    Returns (sample, choices, detail) on success, or None.
    """
    for sample, choices in fuzzer.recorded_samples(
        idl_type, count=MAX_SAMPLES,
    ):
        found, detail = oracle(sample)
        if found:
            return sample, choices, detail
    return None


def shrink_and_report(fuzzer, idl_type, oracle, sample, choices, detail,
                      cve_id, description, browser):
    """Shrink a triggering sample and print the report."""
    def predicate(s):
        found, _ = oracle(s)
        return found

    minimal, minimal_choices = fuzzer.shrink(idl_type, choices, predicate)
    still_valid, minimal_detail = oracle(minimal)

    # If shrinking produced a non-deterministic result (e.g. 0 choices
    # fell back to random generation), use the original as the reproducer.
    if not still_valid:
        minimal = sample
        minimal_choices = choices
        minimal_detail = detail

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

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fuzzer = Fuzzer(idls=(IDL_FILE,))

    cves = [
        {
            'idl_type': 'ImageData',
            'oracle': check_integer_overflow,
            'cve_id': 'CVE-2017-5112',
            'description': 'WebGL readPixels heap buffer overflow (uint32 wrap in sw*sh*4)',
            'browser': 'Chrome < 61',
        },
        {
            'idl_type': 'OscillatorNode',
            'oracle': check_special_float,
            'cve_id': 'CVE-2023-1222',
            'description': 'Web Audio heap buffer overflow from Infinity/NaN params',
            'browser': 'Chrome < 111',
        },
        {
            'idl_type': 'ImageData',
            'oracle': check_zero_dimension,
            'cve_id': 'CVE-2016-1935',
            'description': 'WebGL bufferSubData zero-length buffer OOM',
            'browser': 'Firefox < 44',
        },
    ]

    print('idl2js CVE Hunting Demo')
    print('=' * 64)
    print(f'Generating up to {MAX_SAMPLES} samples per CVE target...\n')

    found_count = 0
    for cve in cves:
        result = hunt_cve(
            fuzzer,
            cve['idl_type'],
            cve['oracle'],
            cve['cve_id'],
            cve['description'],
        )
        if result:
            found_count += 1
            sample, choices, detail = result
            shrink_and_report(
                fuzzer,
                cve['idl_type'],
                cve['oracle'],
                sample, choices, detail,
                cve['cve_id'],
                cve['description'],
                cve['browser'],
            )
        else:
            print(f'\n  {cve["cve_id"]}: not triggered in {MAX_SAMPLES} samples')

    print(f'\nResults: {found_count}/{len(cves)} CVE patterns found and shrunk.')


if __name__ == '__main__':
    main()
