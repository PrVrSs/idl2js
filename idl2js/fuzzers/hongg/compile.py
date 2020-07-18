from distutils.core import setup, Extension

from Cython.Build import cythonize

from idl2js.fuzzers.hongg.const import HONGG_DIR


def make_extension():
    return Extension(
        'honggfuzz',
        ['honggfuzz.pyx'],
        extra_objects=[
            str(HONGG_DIR / 'libhfuzz/libhfuzz.a'),
            str(HONGG_DIR / 'libhfcommon/libhfcommon.a'),
        ],
        include_dirs=[str(HONGG_DIR)],
        libraries=['rt'],
    )


setup(ext_modules=cythonize([make_extension()], language_level=3, cache=False))
