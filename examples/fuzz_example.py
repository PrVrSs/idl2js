import json
from pathlib import Path

from idl2js.fuzzer import Fuzzer
from idl2js.generators.coverage import CoverageTracker


EXAMPLES_DIR = Path(__file__).parent


def fuzz_canvas():
    print('=' * 60)
    print('Fuzzing Canvas API types')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'canvas.webidl')
    coverage = CoverageTracker()
    fuzzer = Fuzzer(idls=(idl_file,), coverage=coverage)

    print('\n--- ImageData (constructor with integer args) ---')
    for sample in fuzzer.samples('ImageData', count=5):
        for instance in sample:
            print(instance)
        print()

    print('\n--- Path2D (constructor with string arg) ---')
    for sample in fuzzer.samples('Path2D', count=3):
        for instance in sample:
            print(instance)
        print()

    print('\n--- CanvasFillRule (enum) ---')
    for sample in fuzzer.samples('CanvasFillRule', count=5):
        for instance in sample:
            print(instance)
        print()

    print('\n--- CanvasRenderingContext2DSettings (dictionary) ---')
    for sample in fuzzer.samples('CanvasRenderingContext2DSettings', count=3):
        for instance in sample:
            print(instance)
        print()

    print('\n--- Coverage Report ---')
    print(json.dumps(coverage.report(), indent=2))


def fuzz_web_audio():
    print('\n')
    print('=' * 60)
    print('Fuzzing Web Audio API types')
    print('=' * 60)

    idl_file = str(EXAMPLES_DIR / 'web_audio.webidl')
    coverage = CoverageTracker()
    fuzzer = Fuzzer(idls=(idl_file,), coverage=coverage)

    print('\n--- OscillatorNode (interface with dependencies) ---')
    for sample in fuzzer.samples('OscillatorNode', count=5):
        for instance in sample:
            print(instance)
        print()

    print('\n--- GainNode ---')
    for sample in fuzzer.samples('GainNode', count=3):
        for instance in sample:
            print(instance)
        print()

    print('\n--- PannerNode (many float parameters) ---')
    for sample in fuzzer.samples('PannerNode', count=3):
        for instance in sample:
            print(instance)
        print()

    print('\n--- OscillatorType (enum) ---')
    for sample in fuzzer.samples('OscillatorType', count=5):
        for instance in sample:
            print(instance)
        print()

    print('\n--- BiquadFilterType (enum with 8 values) ---')
    for sample in fuzzer.samples('BiquadFilterType', count=10):
        for instance in sample:
            print(instance)
        print()

    print('\n--- Coverage Report ---')
    print(json.dumps(coverage.report(), indent=2))


if __name__ == '__main__':
    fuzz_canvas()
    fuzz_web_audio()
