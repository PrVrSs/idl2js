from types import SimpleNamespace

from more_itertools import first_true
from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_interface
from idl2js.visitor import Visitor

from .definition import Interface
from .helper import (
    IDLArgument,
    IDLFunction,
    IDLOptional,
    IDLProperty,
    IDLVariadic,
    prepare_idl_type,
)


class InterfaceVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        interface = self.visit_interface(node)

        return type(
            interface.name,
            (Interface,),
            {
                '__type__': interface.name,
                '__builder__': js_interface,
                '_attributes_': interface.attributes,
                '_constructor_': interface.constructor,
                '_inheritance_': interface.inheritance,
                '__default_opt__': {},
            },
        )

    def visit_interface(self, node):
        constructor = None
        attrs = []

        for member in node.members:
            result = self.visit(member)
            if result is None:
                continue
            if isinstance(result, IDLFunction) and result.name == 'constructor':
                constructor = result
            else:
                attrs.append(result)

        if constructor is None:
            constructor = IDLFunction(name='constructor', return_type='self', arguments=[])

        return SimpleNamespace(
            name=node.name,
            constructor=constructor,
            inheritance=getattr(node, 'inheritance', None),
            namespace=(
                namespace := first_true(
                      node.ext_attrs,
                      pred=lambda attr: attr.name == 'LegacyNamespace',
                )
            ) and namespace.rhs.value,
            attributes=attrs,
        )

    def visit_attribute(self, node):
        return IDLProperty(
            name=node.name,
            value=prepare_idl_type(node.idl_type),
            static=getattr(node, 'special', '') == 'static',
            readonly=getattr(node, 'readonly', False),
        )

    def visit_operation(self, node):
        name = node.name
        if not name:
            special = getattr(node, 'special', '')
            name = f'__{special}__' if special else '__operation__'

        return IDLFunction(
            name=name,
            return_type=prepare_idl_type(node.idl_type),
            arguments=[self.visit(argument) for argument in node.arguments],
            static=getattr(node, 'special', '') == 'static',
        )

    def visit_constructor(self, node):
        return IDLFunction(
            name=node.type,
            return_type='self',
            arguments=[self.visit(argument) for argument in node.arguments],
        )

    def visit_argument(self, node):
        argument_type = prepare_idl_type(node.idl_type)

        if node.optional is True:
            argument_type = IDLOptional(value=argument_type)

        if getattr(node, 'variadic', False):
            argument_type = IDLVariadic(value=argument_type)

        return IDLArgument(
            name=node.name,
            value=argument_type,
            default=extract_default(getattr(node, 'default', None)),
        )

    def visit_const(self, _node):
        return None

    def visit_iterable_(self, _node):
        return None

    def visit_map_like(self, _node):
        return None

    def visit_set_like(self, _node):
        return None


def extract_default(node_default):
    if node_default is None:
        return None
    if hasattr(node_default, 'value'):
        return node_default.value
    return None
