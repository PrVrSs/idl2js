import argparse
import hashlib
import json
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from idl2js.execution import BrowserRunner, DockerRunner
from idl2js.fuzzer import Fuzzer
from idl2js.smt.guided import guided_samples
from idl2js.smt.predicates import (
    GPU_BUFFER_BINDING_OVERFLOW,
    GPU_BUFFER_OVERFLOW,
    GPU_TEXEL_COPY_OVERFLOW,
    GPU_TEXTURE_OVERFLOW,
    GPU_VERTEX_STRIDE_OVERFLOW,
)


EXAMPLES_DIR = Path(__file__).parent

_GC_STRESS = (
    "if (typeof gc === 'function') { "
    "gc({type: 'minor'}); gc({type: 'major'}); gc({type: 'minor'}); "
    "gc(); gc(); }"
)

_GC_INTERLEAVE = "if (typeof gc === 'function') gc();"

_GC_ALLOC_PRESSURE = (
    "{ let _bufs = []; "
    "for (let _i = 0; _i < 20; _i++) _bufs.push(new ArrayBuffer(65536)); "
    "_bufs = null; }"
)

# WebGPU requires a real adapter+device. This preamble requests one and
# falls through gracefully if WebGPU is unavailable.
_WEBGPU_PREAMBLE = """\
let _adapter, _device, _queue;
try {
  _adapter = await navigator.gpu.requestAdapter();
  if (!_adapter) throw new Error('no adapter');
  _device = await _adapter.requestDevice();
  _queue = _device.queue;
} catch(_e) {
  // WebGPU not available — skip
}
if (_device) {
"""

_WEBGPU_EPILOGUE = """\
}
"""


TARGETS = [
    {
        'name': 'GPUBuffer size overflow (>2^31)',
        'idl_file': 'webgpu.webidl',
        'idl_type': 'GPUBuffer',
        'predicate': GPU_BUFFER_OVERFLOW,
        'harness': """\
try {
  const _buf = _device.createBuffer({
    size: {SIZE},
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    mappedAtCreation: true,
  });
  const _arr = new Uint8Array(_buf.getMappedRange());
  _arr[0] = 0x41;
  _arr[_arr.length - 1] = 0x42;
  _buf.unmap();
  _device.destroy();
} catch(_e) {}
""",
        'extract_fn': lambda sample: _extract_dict_field(sample, 'size'),
    },
    {
        'name': 'GPUTexture dimension overflow (w*h*d*4 > 2^32)',
        'idl_file': 'webgpu.webidl',
        'idl_type': 'GPUTexture',
        'predicate': GPU_TEXTURE_OVERFLOW,
        'harness': """\
try {
  const _tex = _device.createTexture({
    size: [{WIDTH}, {HEIGHT}, {DEPTH}],
    format: 'rgba8unorm',
    usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC,
  });
  const _view = _tex.createView();
  _tex.destroy();
} catch(_e) {}
try {
  const _tex2 = _device.createTexture({
    size: [{WIDTH}, {HEIGHT}, {DEPTH}],
    format: 'rgba32float',
    usage: GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.COPY_DST,
  });
  _tex2.destroy();
} catch(_e) {}
""",
        'extract_fn': lambda sample: _extract_extent3d(sample),
    },
    {
        'name': 'GPUTexelCopy layout overflow (offset+bpr*rpi > 2^32)',
        'idl_file': 'webgpu.webidl',
        'idl_type': 'GPUTexture',
        'predicate': GPU_TEXEL_COPY_OVERFLOW,
        'harness': """\
try {
  const _src = _device.createBuffer({
    size: 4096,
    usage: GPUBufferUsage.COPY_SRC | GPUBufferUsage.MAP_WRITE,
    mappedAtCreation: true,
  });
  _src.unmap();
  const _tex = _device.createTexture({
    size: [64, 64, 1],
    format: 'rgba8unorm',
    usage: GPUTextureUsage.COPY_DST,
  });
  const _enc = _device.createCommandEncoder();
  _enc.copyBufferToTexture(
    { buffer: _src, offset: {OFFSET}, bytesPerRow: {BPR}, rowsPerImage: {RPI} },
    { texture: _tex },
    [64, 64, 1],
  );
  _queue.submit([_enc.finish()]);
  _tex.destroy();
  _src.destroy();
} catch(_e) {}
""",
        'extract_fn': lambda sample: _extract_texel_copy(sample),
    },
    {
        'name': 'GPUVertexBuffer stride overflow (>=2^31)',
        'idl_file': 'webgpu.webidl',
        'idl_type': 'GPUTexture',
        'predicate': GPU_VERTEX_STRIDE_OVERFLOW,
        'harness': """\
try {
  const _module = _device.createShaderModule({
    code: `@vertex fn vs(@location(0) p: vec4f) -> @builtin(position) vec4f { return p; }
           @fragment fn fs() -> @location(0) vec4f { return vec4f(1); }`,
  });
  const _pipeline = _device.createRenderPipeline({
    layout: 'auto',
    vertex: {
      module: _module,
      entryPoint: 'vs',
      buffers: [{
        arrayStride: {STRIDE},
        attributes: [{ shaderLocation: 0, offset: 0, format: 'float32x4' }],
      }],
    },
    fragment: {
      module: _module,
      entryPoint: 'fs',
      targets: [{ format: 'rgba8unorm' }],
    },
  });
} catch(_e) {}
""",
        'extract_fn': lambda sample: _extract_dict_field(sample, 'arrayStride'),
    },
    {
        'name': 'GPUBufferBinding offset+size overflow (>2^32)',
        'idl_file': 'webgpu.webidl',
        'idl_type': 'GPUTexture',
        'predicate': GPU_BUFFER_BINDING_OVERFLOW,
        'harness': """\
try {
  const _buf = _device.createBuffer({
    size: 256,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
  });
  const _bgl = _device.createBindGroupLayout({
    entries: [{ binding: 0, visibility: GPUShaderStage.VERTEX, buffer: { type: 'uniform' } }],
  });
  const _bg = _device.createBindGroup({
    layout: _bgl,
    entries: [{ binding: 0, resource: { buffer: _buf, offset: {OFFSET}, size: {SIZE} } }],
  });
  _buf.destroy();
} catch(_e) {}
""",
        'extract_fn': lambda sample: _extract_buffer_binding(sample),
    },
]


# ---------------------------------------------------------------------------
# Value extraction helpers
# ---------------------------------------------------------------------------

def _extract_dict_field(sample, field_name):
    pat = re.compile(re.escape(field_name) + r':\s*\w+')
    val_pat = re.compile(r'= (\d+)')
    for inst in sample:
        s = str(inst)
        if field_name in s and '=' in s:
            m = val_pat.search(s)
            if m:
                return m.group(1)
    return None


def _extract_extent3d(sample):
    vals = {}
    for inst in sample:
        s = str(inst)
        for field in ('width', 'height', 'depthOrArrayLayers'):
            if field + ':' in s:
                continue
            # look for variable assignment
        m = re.search(r'= (\d+)', s)
        if m:
            # match by dict field
            if 'width:' in s or 'height:' in s or 'depthOrArrayLayers:' in s:
                pass
    # Fallback: scan for the dict construction with width/height/depth
    for inst in sample:
        s = str(inst)
        if 'width:' in s and 'height:' in s:
            w_m = re.search(r'width:\s*(\w+)', s)
            h_m = re.search(r'height:\s*(\w+)', s)
            d_m = re.search(r'depthOrArrayLayers:\s*(\w+)', s)
            if w_m:
                vals['width_var'] = w_m.group(1)
            if h_m:
                vals['height_var'] = h_m.group(1)
            if d_m:
                vals['depth_var'] = d_m.group(1)

    # Resolve variable values
    var_vals = {}
    for inst in sample:
        s = str(inst)
        m = re.match(r'try \{(\w+) = (\d+)\}', s)
        if m:
            var_vals[m.group(1)] = m.group(2)

    w = var_vals.get(vals.get('width_var', ''), '256')
    h = var_vals.get(vals.get('height_var', ''), '256')
    d = var_vals.get(vals.get('depth_var', ''), '1')
    return {'width': w, 'height': h, 'depth': d}


def _extract_texel_copy(sample):
    from idl2js.smt.solver import SMTSolver
    from idl2js.smt.predicates import GPU_TEXEL_COPY_OVERFLOW
    solver = SMTSolver(GPU_TEXEL_COPY_OVERFLOW)
    result = solver.solve()
    if result:
        return {
            'offset': str(result.get('offset', 0)),
            'bpr': str(result.get('bytesPerRow', 256)),
            'rpi': str(result.get('rowsPerImage', 1)),
        }
    return {'offset': '0', 'bpr': '256', 'rpi': '1'}


def _extract_buffer_binding(sample):
    from idl2js.smt.solver import SMTSolver
    from idl2js.smt.predicates import GPU_BUFFER_BINDING_OVERFLOW
    solver = SMTSolver(GPU_BUFFER_BINDING_OVERFLOW)
    result = solver.solve()
    if result:
        return {
            'offset': str(result.get('offset', 0)),
            'size': str(result.get('size', 256)),
        }
    return {'offset': '0', 'size': '256'}


# ---------------------------------------------------------------------------
# ASAN report parser
# ---------------------------------------------------------------------------

def parse_asan_report(stderr):
    if not stderr:
        return None

    bug_pat = re.compile(r'ERROR: (?:Address|Thread|Memory)Sanitizer: (\S+)')
    frame_pat = re.compile(r'#(\d+)\s+0x[0-9a-fA-F]+\s+in\s+(\S+)')

    bug_match = bug_pat.search(stderr)
    bug_type = bug_match.group(1) if bug_match else None

    frames = []
    for m in frame_pat.finditer(stderr):
        func = m.group(2)
        func = re.sub(r'<[^>]*>', '', func)
        frames.append(func)

    if not bug_type and not frames:
        # Check for signal-based crash
        sig_pat = re.compile(r'Received signal (\d+)')
        sig_m = sig_pat.search(stderr)
        if sig_m:
            bug_type = f'signal-{sig_m.group(1)}'
        else:
            return None

    top3 = frames[:3]
    fingerprint_src = f'{bug_type}:{"!".join(top3)}'
    fingerprint = hashlib.sha256(fingerprint_src.encode()).hexdigest()[:12]

    return {
        'bug_type': bug_type,
        'frames': frames[:10],
        'fingerprint': fingerprint,
    }


# ---------------------------------------------------------------------------
# Harness builder
# ---------------------------------------------------------------------------

def build_harness(target, sample, extract_vals):
    poc_js = '\n'.join(str(inst) for inst in sample)

    harness = target['harness']
    if isinstance(extract_vals, dict):
        for key, val in extract_vals.items():
            harness = harness.replace('{' + key.upper() + '}', str(val))
    elif extract_vals is not None:
        harness = harness.replace('{SIZE}', str(extract_vals))
        harness = harness.replace('{STRIDE}', str(extract_vals))

    parts = [
        '(async () => {',
        _WEBGPU_PREAMBLE,
        _GC_INTERLEAVE,
        poc_js,
        _GC_INTERLEAVE,
        harness,
        _GC_STRESS,
        _GC_ALLOC_PRESSURE,
        _WEBGPU_EPILOGUE,
        '})();',
    ]
    return '\n'.join(parts)


def save_finding(findings_dir, target, kind, poc_js, detail, outcome):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    name = f'webgpu_{target["name"][:30].replace(" ", "_")}_{kind}_{ts}'
    out = Path(findings_dir) / name
    out.mkdir(parents=True, exist_ok=True)
    (out / 'poc.js').write_text(poc_js, encoding='utf-8')
    stderr_text = getattr(outcome, 'stderr', '') or ''
    asan = parse_asan_report(stderr_text)
    meta = {
        'name': target['name'],
        'kind': kind,
        'exit_code': getattr(outcome, 'exit_code', None),
        'signal': getattr(outcome, 'signal', None),
        'duration_ms': getattr(outcome, 'duration_ms', None),
        'stderr': stderr_text[:8000],
        'asan_bug_type': asan['bug_type'] if asan else None,
        'asan_fingerprint': asan['fingerprint'] if asan else None,
        'asan_frames': asan['frames'] if asan else None,
    }
    (out / 'detail.json').write_text(
        json.dumps(meta, indent=2), encoding='utf-8',
    )
    return out, asan


def main():
    parser = argparse.ArgumentParser(
        description='SMT-guided WebGPU ASAN fuzzer',
    )
    parser.add_argument('--docker-image', metavar='IMAGE')
    parser.add_argument('--chrome', metavar='PATH')
    parser.add_argument('--browser', choices=['chrome', 'firefox'], default='chrome')
    parser.add_argument('--timeout', type=int, default=20000)
    parser.add_argument('--samples-per-target', type=int, default=50)
    parser.add_argument('--findings-dir', default='findings')
    parser.add_argument('--continuous', action='store_true')
    parser.add_argument('--target', metavar='NAME')
    args = parser.parse_args()

    if not args.docker_image and not args.chrome:
        print('Error: specify --docker-image or --chrome')
        sys.exit(1)

    is_firefox = args.browser == 'firefox'
    if is_firefox:
        browser_path = '/opt/firefox/firefox'
        browser_args = ['-profile', '/tmp/ff-profile', '--headless', '--no-remote']
        docker_args = ['--shm-size=2g', '--memory=4g', '--memory-swap=4g']
    else:
        browser_path = '/opt/chromium/chrome'
        browser_args = ['--headless', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--enable-unsafe-webgpu',
                        '--enable-features=Vulkan,UseSkiaRenderer']
        docker_args = ['--network=none', '--shm-size=256m',
                       '--memory=4g', '--memory-swap=4g']

    if args.docker_image:
        runner = DockerRunner(
            image=args.docker_image,
            chrome_path=browser_path,
            chrome_args=browser_args,
            timeout_ms=args.timeout,
            docker_args=docker_args,
        )
        print(f'[+] DockerRunner(image={args.docker_image}, browser={args.browser})')
    else:
        runner = BrowserRunner(
            chrome_path=args.chrome or browser_path,
            chrome_args=browser_args,
            timeout_ms=args.timeout,
        )
        print(f'[+] BrowserRunner(chrome={args.chrome or browser_path})')

    targets = TARGETS
    if args.target:
        targets = [t for t in TARGETS if args.target.lower() in t['name'].lower()]
        if not targets:
            print(f'No targets matching "{args.target}"')
            sys.exit(1)

    findings_dir = Path(args.findings_dir)
    findings_dir.mkdir(parents=True, exist_ok=True)

    stop = [False]

    def _stop_handler(_sig, _frame):
        print('\n[!] Stopping...')
        stop[0] = True

    signal.signal(signal.SIGINT, _stop_handler)
    signal.signal(signal.SIGTERM, _stop_handler)

    seen_crashes = set()
    stats = {'total': 0, 'executed': 0, 'crashes': 0, 'unique': 0, 'timeouts': 0}

    print(f'[*] WebGPU ASAN fuzzer — {len(targets)} targets')
    print(f'[*] {args.samples_per_target} samples/target/round | findings → {findings_dir}')
    print()

    start = time.monotonic()
    round_num = 0

    while not stop[0]:
        round_num += 1
        print(f'--- Round {round_num} ---')

        for target in targets:
            if stop[0]:
                break

            idl_path = str(EXAMPLES_DIR / target['idl_file'])
            fuzzer = Fuzzer(idls=(idl_path,))
            predicate = target['predicate']

            sample_count = 0
            for sample, choices in guided_samples(
                fuzzer, target['idl_type'], predicate,
                count=args.samples_per_target,
            ):
                if stop[0]:
                    break

                stats['total'] += 1
                sample_count += 1

                extract_vals = target['extract_fn'](sample)
                poc_js = build_harness(target, sample, extract_vals)

                outcome = runner.run(poc_js)
                stats['executed'] += 1

                if outcome.is_crash:
                    stats['crashes'] += 1
                    asan = parse_asan_report(outcome.stderr)
                    fp = asan['fingerprint'] if asan else None

                    if fp and fp in seen_crashes:
                        print(f'  [DUP] {target["name"]} fp={fp}')
                        continue

                    if fp:
                        seen_crashes.add(fp)
                    stats['unique'] += 1

                    out, _ = save_finding(
                        findings_dir, target, 'crash',
                        poc_js, predicate.name, outcome,
                    )

                    print(f'\n{"!" * 68}')
                    print(f'  [CRASH] {target["name"]}')
                    print(f'  signal={outcome.signal}  '
                          f'duration={outcome.duration_ms:.0f}ms')
                    if asan:
                        print(f'  ASAN: {asan["bug_type"]}  fp={fp}')
                        if asan['frames']:
                            print(f'  stack: {" -> ".join(asan["frames"][:5])}')
                    print(f'  saved: {out}')
                    if outcome.stderr:
                        print(f'  stderr: {outcome.stderr[:400]}')
                    print(f'{"!" * 68}\n')

                elif outcome.is_timeout:
                    stats['timeouts'] += 1
                    if stats['timeouts'] <= 5:
                        save_finding(
                            findings_dir, target, 'timeout',
                            poc_js, predicate.name, outcome,
                        )
                        print(f'  [TIMEOUT] {target["name"]}')

                elif sample_count % 10 == 0:
                    elapsed = time.monotonic() - start
                    rate = stats['executed'] / elapsed if elapsed > 0 else 0
                    print(f'  [{target["name"][:30]}] '
                          f'{sample_count}/{args.samples_per_target}  '
                          f'total={stats["executed"]}  '
                          f'{rate:.1f} exec/s  '
                          f'crashes={stats["crashes"]} '
                          f'(unique={stats["unique"]})')

        if not args.continuous:
            break

    elapsed = time.monotonic() - start
    rate = stats['executed'] / elapsed if elapsed > 0 else 0
    print(f'\n{"=" * 68}')
    print(f'Done — {elapsed:.1f}s')
    print(f'  Generated:  {stats["total"]}')
    print(f'  Executed:   {stats["executed"]} ({rate:.1f}/s)')
    print(f'  Crashes:    {stats["crashes"]} ({stats["unique"]} unique)')
    print(f'  Timeouts:   {stats["timeouts"]}')
    print(f'  Findings:   {findings_dir}')


if __name__ == '__main__':
    main()
