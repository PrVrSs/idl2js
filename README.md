# idl2js

**Grammar-based Fuzzer that uses WebIDL as a grammar.**

[![Build Status](https://img.shields.io/travis/PrVrSs/idl2js/master?style=plastic)](https://travis-ci.org/github/PrVrSs/idl2js)
[![Codecov](https://img.shields.io/codecov/c/github/PrVrSs/idl2js?style=plastic)](https://codecov.io/gh/PrVrSs/idl2js)
[![Python Version](https://img.shields.io/badge/python-3.10-blue?style=plastic)](https://www.python.org/)
[![License](https://img.shields.io/cocoapods/l/A?style=plastic)](https://github.com/PrVrSs/idl2js/blob/master/LICENSE)


## Quick start

```shell script
pip install idl2js
```


### Build from source

*Get source and install dependencies*
```shell script
git clone https://gitlab.com/PrVrSs/idl2js.git
cd idl2js
poetry install
```

*Run tests*
```shell script
make unit
```


### Examples

```python
from pathlib import Path
from pprint import pprint

from idl2js import Fuzzer


def main():
    fuzzer = Fuzzer(
        idls=[
            str((Path(__file__).parent / 'Blob.webidl').resolve()),
        ])

    pprint(list(fuzzer.samples(
        idl_type='Blob',
        options={
            'DOMString': {
                'min_codepoint': 97,
                'max_codepoint': 122,
                'include_categories': {},
            }
        }
    )))


if __name__ == '__main__':
    main()

```


#### Output

```js
try {v_0805c1325a3048aca879de7ce5f8c9a5 = new Int8Array()} catch(e){}
try {v_cfa435d6211f41df8a6af0a8543b3b37 = new WebAssembly.Module(v_0805c1325a3048aca879de7ce5f8c9a5)} catch(e){}
try {v_5deaeb375b774b54b6140be12322296a = {value: 'v128', mutable: true}} catch(e){}
try {v_788c98fd9d97444688f48fedb824130b = 'meoein'} catch(e){}
try {v_c3fcd21aecdd4ef6bb2060cbb0bd70fb = new WebAssembly.Global(v_5deaeb375b774b54b6140be12322296a, v_788c98fd9d97444688f48fedb824130b)} catch(e){}
try {v_73a4bd166ae34681a13acc70c2a67876 = {element: 'anyfunc', initial: 290477176, maximum: 3297392043}} catch(e){}
try {v_061571cb277b42beb33546c8d8c3ed07 = 'pahfbx'} catch(e){}
try {v_0c4bc44857394e40a9ade62f0eaadfca = new WebAssembly.Table(v_73a4bd166ae34681a13acc70c2a67876, v_061571cb277b42beb33546c8d8c3ed07)} catch(e){}
try {v_06ab1c4441d543ae8d4289c13a07c895 = {initial: 2477011723, maximum: 3809510539}} catch(e){}
try {v_5e251ff6ba8647e48a2d633ba42386f8 = new WebAssembly.Memory(v_06ab1c4441d543ae8d4289c13a07c895)} catch(e){}
```


### Links

* [searchfox - webidl](https://searchfox.org/mozilla-central/source/dom/webidl)
* [original webidl parser](https://github.com/w3c/webidl2.js)
* [TSJS-lib-generator](https://github.com/microsoft/TSJS-lib-generator/tree/master/inputfiles/idl)
* [ECMAScript® 2021 Language Specification](https://tc39.es/ecma262/)
* [Web IDL Spec](https://webidl.spec.whatwg.org/)


## Contributing

Any help is welcome and appreciated.


## License

*idl2js* is licensed under the terms of the Apache-2.0 License (see the file LICENSE).
