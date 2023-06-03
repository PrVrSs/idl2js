from types import SimpleNamespace

from more_itertools import first_true
from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_interface
from idl2js.idl_types.generic import Interface
from idl2js.idl_types.helper import IDLArgument, IDLFunction, IDLOptional, IDLProperty
from idl2js.visitors.utils import prepare_idl_type
from idl2js.visitors.visitor import Visitor


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
                '__default_opt__': {},
            },
        )

    def visit_interface(self, node):
        constructor, *attrs = [self.visit(member) for member in node.members]

        return SimpleNamespace(
            name=node.name,
            constructor=constructor,
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
            value=prepare_idl_type(node.idl_type)
        )

    def visit_operation(self, node):
        return IDLFunction(
            name=node.name,
            return_type=prepare_idl_type(node.idl_type),
            arguments=[self.visit(argument) for argument in node.arguments],
        )

    def visit_constructor(self, node) -> None:
        return IDLFunction(
            name=node.type,
            return_type='self',
            arguments=[self.visit(argument) for argument in node.arguments],
        )

    def visit_argument(self, node):
        argument_type = prepare_idl_type(node.idl_type)

        if node.optional is True:
            argument_type = IDLOptional(value=argument_type)

        return IDLArgument(name=node.name, value=argument_type)
