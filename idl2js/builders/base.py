from idl2js.js.statements import create_literal


def js_literal(idl_type):
    return create_literal(idl_type.generate())
