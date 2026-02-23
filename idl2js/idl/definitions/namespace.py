from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_namespace
from idl2js.visitor import Visitor

from .definition import Namespace_
from .helper import IDLArgument, IDLFunction, IDLOptional, IDLProperty, prepare_idl_type


class NamespaceVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        namespace = self.visit_namespace(node)

        return type(
            namespace.name,
            (Namespace_,),
            {
                '__type__': namespace.name,
                '__builder__': js_namespace,
                '_attributes_': namespace.attributes,
                '_constructor_': IDLFunction(
                    name='constructor', return_type='self', arguments=[],
                ),
                '__default_opt__': {},
            },
        )

    def visit_namespace(self, node):
        attrs = []
        for member in node.members:
            result = self.visit(member)
            if result is not None:
                attrs.append(result)

        return SimpleNamespace(
            name=node.name,
            attributes=attrs,
        )

    def visit_attribute(self, node):
        return IDLProperty(
            name=node.name,
            value=prepare_idl_type(node.idl_type),
            readonly=getattr(node, 'readonly', False),
        )

    def visit_operation(self, node):
        return IDLFunction(
            name=node.name or '__operation__',
            return_type=prepare_idl_type(node.idl_type),
            arguments=[self.visit(argument) for argument in node.arguments],
        )

    def visit_argument(self, node):
        argument_type = prepare_idl_type(node.idl_type)

        if node.optional is True:
            argument_type = IDLOptional(value=argument_type)

        return IDLArgument(name=node.name, value=argument_type)

    def visit_const(self, _node):
        return None
