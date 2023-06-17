# idl2js

**Grammar-based Fuzzer that uses WebIDL as a grammar.**

[![Build Status](https://github.com/PrVrSs/idl2js/workflows/test/badge.svg?branch=master&event=push)](https://github.com/PrVrSs/idl2js/actions?query=workflow%3Atest)
[![Codecov](https://img.shields.io/codecov/c/github/PrVrSs/idl2js)](https://codecov.io/gh/PrVrSs/idl2js)
[![Python Version](https://img.shields.io/badge/python-3.10%20|%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/cocoapods/l/A)](https://github.com/PrVrSs/idl2js/blob/master/LICENSE)


## Quick start

```bash
pip install idl2js
```


### Build from source

*Get source and install dependencies*
```bash
git clone https://gitlab.com/PrVrSs/idl2js.git
cd idl2js
poetry install
```

*Run tests*
```bash
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
            # https://www.w3.org/TR/wasm-js-api-2/#idl-index
            str((Path(__file__).parent / 'webassembly.webidl').resolve()),
        ])

    pprint(list(fuzzer.samples(
        idl_type='Table',
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
[[try {v_cd820bf385f14b2383dfb7f81a4f935b = 'anyfunc'} catch(e){},
  try {v_efa5137be7fe4063bf47252046aa0d74 = 2017893174} catch(e){},
  try {v_646b30b73c6c4238945f1a4390ce73c8 = 4237930728} catch(e){},
  try {v_39b62d49860248c5bcc5a904ac7bc277 = {element: 'v_cd820bf385f14b2383dfb7f81a4f935b', initial: 'v_efa5137be7fe4063bf47252046aa0d74', maximum: 'v_646b30b73c6c4238945f1a4390ce73c8'}} catch(e){},
  try {v_ba1287fff1984465ad2ec78abb6c5b3f = 3981072889} catch(e){},
  try {v_ccc9de6d2e64407bb78f1ca330563fb7 = new Table('v_39b62d49860248c5bcc5a904ac7bc277', 'v_ba1287fff1984465ad2ec78abb6c5b3f')} catch(e){}],
 [try {v_29ad83a7ef134d48bc10a2057721d811 = 'anyfunc'} catch(e){},
  try {v_fe5d92a6347b4799948eaf0e7f3901ae = 3273608333} catch(e){},
  try {v_8a274ed057464448a103c554bb0f4489 = 1287757149} catch(e){},
  try {v_1d7a983af8754a09adc7079bccca71df = {element: 'v_29ad83a7ef134d48bc10a2057721d811', initial: 'v_fe5d92a6347b4799948eaf0e7f3901ae', maximum: 'v_8a274ed057464448a103c554bb0f4489'}} catch(e){},
  try {v_08efc03de63a4ab8ae0f0a3010eaa7b9 = 3191963624} catch(e){},
  try {v_3436efc34ef3426bb05902a989cdde3c = new Table('v_1d7a983af8754a09adc7079bccca71df', 'v_08efc03de63a4ab8ae0f0a3010eaa7b9')} catch(e){}],
 [try {v_7eeb3f14281f4223beeb48d3e0739b4b = 'externref'} catch(e){},
  try {v_bf5605aa5293417a9fc90fc9d875fe4e = 3573454083} catch(e){},
  try {v_22df38f875364571abd808b0a8c81b73 = 3093703977} catch(e){},
  try {v_6158fc93b00b4dd8a0e9b56092ea32a5 = {element: 'v_7eeb3f14281f4223beeb48d3e0739b4b', initial: 'v_bf5605aa5293417a9fc90fc9d875fe4e', maximum: 'v_22df38f875364571abd808b0a8c81b73'}} catch(e){},
  try {v_d259852980f04de1a1915ac3ec9f5686 = 2563963223} catch(e){},
  try {v_88487080d56c4fa08630f5698f87bb70 = new Table('v_6158fc93b00b4dd8a0e9b56092ea32a5', 'v_d259852980f04de1a1915ac3ec9f5686')} catch(e){}]]
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
