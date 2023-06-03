from idl2js.js.instance import Instance as JSInstance
from idl2js.js.statements import create_literal, create_object
from idl2js.utils import unique_name


def js_literal(idl_type):
    return create_literal(idl_type.generate())


def js_interface(idl_type, arguments, name: str = None):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_object(
            name=name or unique_name(),
            progenitor=idl_type.__type__,
            arguments=arguments,
        ),
    )
