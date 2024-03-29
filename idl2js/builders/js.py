from idl2js.js.instance import Instance as JSInstance
from idl2js.js.statements import (
    create_array,
    create_dict,
    create_expression,
    create_literal,
    create_object,
    create_property,
)
from idl2js.utils import unique_name


def js_literal(idl_type, *_):
    expression = idl_type.generate()
    if isinstance(expression, list):
        expression = create_array([create_literal(expr) for expr in expression])
    else:
        expression = create_literal(expression)

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


def js_type_def(idl_type, *args):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_expression(
            name=unique_name(),
            expression=create_literal(args[0][0]),
        )
    )


def js_enum(idl_type, *_):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_expression(
            name=unique_name(),
            expression=create_literal(idl_type.generate()),
        )
    )


def js_dictionary(idl_type, *args):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_dict(
            name=unique_name(),
            properties=[
                create_property(
                    key=name,
                    value=create_literal(arg),
                )
                for name, arg in zip(idl_type.attr_name(), args[0])
            ]
        )
    )
