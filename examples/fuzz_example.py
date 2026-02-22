import json
from pathlib import Path

from idl2js.fuzzer import Fuzzer
from idl2js.generators.coverage import CoverageTracker
from idl2js.generators.database import ExampleDatabase


EXAMPLES_DIR = Path(__file__).parent


def fuzz_canvas():
    print('=' * 60)
    print('1. Basic fuzzing with coverage')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'canvas.webidl')
    coverage = CoverageTracker()
    fuzzer = Fuzzer(idls=(idl_file,), coverage=coverage)

    print('\n--- ImageData samples ---')
    for sample in fuzzer.samples('ImageData', count=3):
        for instance in sample:
            print(instance)
        print()

    print('\n--- CanvasFillRule enum ---')
    for sample in fuzzer.samples('CanvasFillRule', count=5):
        for instance in sample:
            print(instance)

    print('\n--- Coverage Report ---')
    print(json.dumps(coverage.report(), indent=2))


def fuzz_with_recording():
    print('\n')
    print('=' * 60)
    print('2. Recording + Replay (Hypothesis-inspired)')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'web_audio.webidl')
    fuzzer = Fuzzer(idls=(idl_file,))

    print('\n--- Record OscillatorNode generation ---')
    for sample, choices in fuzzer.recorded_samples(
        'OscillatorNode', count=1, seed=42,
    ):
        print('Generated:')
        for instance in sample:
            print(f'  {instance}')
        print(f'\nRecorded {len(choices)} random choices')

        print('\n--- Replay same choices ---')
        replayed = fuzzer.replay('OscillatorNode', choices)
        print('Replayed:')
        for instance in replayed:
            print(f'  {instance}')


def fuzz_with_shrinking():
    print('\n')
    print('=' * 60)
    print('3. Shrinking (find minimal reproducer)')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'web_audio.webidl')
    fuzzer = Fuzzer(idls=(idl_file,))

    print('\n--- Find and shrink a PannerNode with large values ---')
    for sample, choices in fuzzer.recorded_samples(
        'PannerNode', count=10, seed=123,
    ):
        has_large = any(
            '1e+' in str(inst) or 'inf' in str(inst).lower()
            for inst in sample
        )
        if has_large:
            print(f'Found sample with large values ({len(choices)} choices)')
            print('Original:')
            for inst in sample:
                text = str(inst)
                if '1e+' in text or 'inf' in text.lower():
                    print(f'  {inst}')

            def predicate(s):
                return any(
                    'inf' in str(i).lower() for i in s
                )

            minimal, minimal_choices = fuzzer.shrink(
                'PannerNode', choices, predicate,
            )
            print(f'\nShrunk to {len(minimal_choices)} choices')
            print('Minimal reproducer:')
            for inst in minimal:
                print(f'  {inst}')
            break


def fuzz_with_database():
    print('\n')
    print('=' * 60)
    print('4. Database (persist interesting examples)')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'canvas.webidl')
    fuzzer = Fuzzer(idls=(idl_file,))
    db = ExampleDatabase(base_path='/tmp/idl2js_example_db')
    db.clear()

    print('\n--- Save interesting ImageData examples ---')
    saved = 0
    for sample, choices in fuzzer.recorded_samples(
        'ImageData', count=20, seed=77,
    ):
        has_boundary = any('= 0}' in str(inst) for inst in sample)
        if has_boundary:
            db.save(
                'ImageData:boundary',
                choices,
                metadata={'reason': 'contains boundary value'},
            )
            saved += 1

    print(f'Saved {saved} interesting examples')

    print('\n--- Replay from database ---')
    for entry in db.fetch('ImageData:boundary')[:2]:
        replayed = fuzzer.replay('ImageData', entry['choices'])
        print(f"Replayed ({entry['metadata']['reason']}):")
        for inst in replayed:
            print(f'  {inst}')
        print()

    db.clear()


if __name__ == '__main__':
    fuzz_canvas()
    fuzz_with_recording()
    fuzz_with_shrinking()
    fuzz_with_database()
