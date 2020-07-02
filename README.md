# idl2js

[![Build Status](https://img.shields.io/travis/com/PrVrSs/idl2js/master?style=plastic)](https://travis-ci.org/github/PrVrSs/idl2js)
[![Codecov](https://img.shields.io/codecov/c/github/PrVrSs/idl2js?style=plastic)](https://codecov.io/gh/PrVrSs/idl2js)
[![Python Version](https://img.shields.io/badge/python-3.8-blue?style=plastic)](https://www.python.org/)
[![License](https://img.shields.io/cocoapods/l/A?style=plastic)](https://github.com/PrVrSs/idl2js/blob/master/LICENSE)

## Description

Grammar-based Fuzzer that uses WebIDL as a grammar.

### Example

*[WebIdl](/examples/raw.webidl)* → *[WebIdlAst](/examples/webidl_ast.json)* → *[JsAst](/examples/js_ast.json)* → *[Js](examples/result.js)*


### RoadMap

- [x] WebIdl Parser
- [ ] WebIdlAst → JsAst
- [ ] Unparse JsAst


### Links


* [searchfox - webidl](https://searchfox.org/mozilla-central/source/dom/webidl)
* [original webidl parser](https://github.com/w3c/webidl2.js)