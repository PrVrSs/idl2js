from idl2js.js.instance import Instance as JSInstance
from idl2js.js.statements import create_array, create_expression, create_literal, create_object
from idl2js.utils import unique_name


def js_literal(idl_type, *_):
    if idl_type.is_sequence():
        expression = create_array([create_literal(idl_type.generate())])
    else:
        expression = create_literal(idl_type.generate())

    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_expression(
            name=unique_name(),
            expression=expression,
        )
    )


def js_interface(idl_type, *args):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_object(
            name=unique_name(),
            progenitor=idl_type.__type__,
            arguments=[
                create_literal(argument)
                for argument in args[0]
            ],
        ),
    )
