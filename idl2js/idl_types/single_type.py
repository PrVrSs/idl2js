from idl2js.generators.generator import CharGenerator
from idl2js.idl_types.base import IdlType, internal_types


class DOMString(IdlType):
    __internal__ = True
    __type__ = 'DOMString'
    __builder__ = CharGenerator


class USVString(IdlType):
    __internal__ = True
    __type__ = 'USVString'
    __builder__ = CharGenerator


if __name__ == '__main__':
    print(internal_types['DOMString'](builder_opt={
        'min_codepoint': 0,
        'max_codepoint': 128,
        'include_categories': {'Lu'},
    }).build())
