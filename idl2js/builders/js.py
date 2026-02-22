from idl2js.idl.base import internal_types
from idl2js.idl.definitions.helper import IDLFunction, IDLType, get_base_type
from idl2js.js.instance import Instance as JSInstance
from idl2js.js.nodes import Identifier, MemberExpression, ObjectExpression
from idl2js.js.statements import (
    create_array,
    create_arrow_function,
    create_dict,
    create_expression,
    create_for_loop,
    create_identifier,
    create_literal,
    create_null_literal,
    create_object,
    create_operation,
    create_property,
    create_property_assignment,
)
from idl2js.utils import unique_name


def _find_method(type_cls, method_name):
    for attr in getattr(type_cls, '_attributes_', []):
        if isinstance(attr, IDLFunction) and attr.name == method_name:
            return attr
    return None


def _generate_arg_instances(method, type_vars):
    arg_nodes = []
    extra_instances = []

    for arg in method.arguments:
        base_type_name, flags = get_base_type(arg.value)

        if base_type_name in type_vars:
            arg_nodes.append(create_identifier(type_vars[base_type_name]))
            continue

        if base_type_name in internal_types:
            std_cls = internal_types[base_type_name]
            value = std_cls({}, flags).generate()
            name = unique_name()
            extra_instances.append(JSInstance(
                idl_type=base_type_name,
                ast=create_expression(name=name, expression=create_literal(value)),
            ))
            arg_nodes.append(create_identifier(name))
            continue

        arg_nodes.append(create_identifier(unique_name()))

    return arg_nodes, extra_instances


def _resolve_arg_spec(arg_spec, type_vars):
    if isinstance(arg_spec, str):
        if arg_spec in type_vars:
            return create_identifier(type_vars[arg_spec])
        return create_identifier(arg_spec)
    if isinstance(arg_spec, dict) and 'prop' in arg_spec:
        of_var = type_vars.get(arg_spec['of'], arg_spec['of'])
        return MemberExpression(
            object=Identifier(name=of_var),
            property=Identifier(name=arg_spec['prop']),
        )
    return create_literal(arg_spec)


def _build_call_action(action, idl_type, type_vars, env):  # pylint: disable=too-many-locals
    instances = []

    on_type_name = action.get('on')
    if on_type_name:
        on_type_cls = env.get_type(on_type_name) if env else None
        obj_var = type_vars.get(on_type_name)
    else:
        on_type_cls = type(idl_type)
        obj_var = type_vars.get(idl_type.__type__)

    method_name = action['method']
    method = _find_method(on_type_cls, method_name)

    explicit_args = action.get('args')
    if explicit_args is not None:
        arg_nodes = [_resolve_arg_spec(a, type_vars) for a in explicit_args]
    elif method:
        arg_nodes, extra = _generate_arg_instances(method, type_vars)
        instances.extend(extra)
    else:
        arg_nodes = []

    result_name = unique_name()
    call_ast = create_operation(
        name=result_name,
        progenitor=obj_var,
        method=method_name,
        arguments=arg_nodes,
    )

    return_type = None
    if method:
        rt = method.return_type
        if isinstance(rt, IDLType):
            return_type = rt.value
        elif isinstance(rt, str) and rt not in ('undefined', 'self'):
            return_type = rt

    inst = JSInstance(
        idl_type=return_type or method_name,
        ast=call_ast,
    )
    instances.append(inst)

    if return_type and return_type != 'undefined':
        type_vars[return_type] = result_name

    return instances


def _resolve_value_expr(value, type_vars):
    if value is None:
        return create_null_literal()
    if isinstance(value, str) and value in type_vars:
        return create_identifier(type_vars[value])
    return create_literal(value)


def _build_set_action(action, type_vars):
    obj_var = type_vars.get(action['on'])
    value_expr = _resolve_value_expr(action['value'], type_vars)
    ast = create_property_assignment(obj_var, action['prop'], value_expr)
    return JSInstance(idl_type=action['on'], ast=ast)


def _build_loop_action(action, type_vars):
    body_stmts = []
    for body_action in action['body']:
        if body_action['kind'] == 'set':
            obj_var = type_vars.get(body_action['on'])
            value_expr = _resolve_value_expr(body_action['value'], type_vars)
            body_stmts.append(
                create_property_assignment(obj_var, body_action['prop'], value_expr)
            )

    loop_ast = create_for_loop('v_i', action['iterations'], body_stmts)
    return JSInstance(idl_type='loop', ast=loop_ast)


def js_literal(idl_type, *_):
    expression = idl_type.generate()
    if isinstance(expression, list):
        expression = create_array([create_literal(expr) for expr in expression])
    elif isinstance(expression, dict):
        expression = ObjectExpression()
    elif isinstance(expression, str) and expression.startswith('Symbol('):
        expression = create_identifier(expression)
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
    constructor = JSInstance(
        idl_type=idl_type.__type__,
        ast=create_object(
            name=unique_name(),
            progenitor=idl_type.__type__,
            arguments=[
                create_identifier(argument)
                for argument in args[0]
            ],
        ),
    )

    builder_opt = idl_type._builder_opt  # pylint: disable=protected-access
    post_actions = builder_opt.get('post_actions')
    if not post_actions:
        return constructor

    env = builder_opt.get('_env')
    type_vars = {idl_type.__type__: constructor.name}

    instances = [constructor]

    for action in post_actions:
        kind = action['kind']
        if kind == 'call':
            instances.extend(_build_call_action(action, idl_type, type_vars, env))
        elif kind == 'set':
            instances.append(_build_set_action(action, type_vars))
        elif kind == 'loop':
            instances.append(_build_loop_action(action, type_vars))

    return instances


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
                    value=create_identifier(arg),
                )
                for name, arg in zip(idl_type.attr_name(), args[0])
            ]
        )
    )


def js_callback(idl_type, *args):
    params = [create_identifier(f'arg{i}') for i in range(len(args[0]))] if args[0] else []
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_expression(
            name=unique_name(),
            expression=create_arrow_function(params=params),
        )
    )


def js_namespace(idl_type, *_):
    return JSInstance(
        idl_type=idl_type.__type__,
        ast=create_expression(
            name=unique_name(),
            expression=create_identifier(idl_type.__type__),
        )
    )
