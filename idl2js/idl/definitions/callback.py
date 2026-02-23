from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_callback
from idl2js.visitor import Visitor

from .definition import Callback_
from .helper import IDLArgument, IDLFunction, IDLOptional, prepare_idl_type


class CallbackVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        callback = self.visit_callback(node)

        return type(
            callback.name,
            (Callback_,),
            {
                '__type__': callback.name,
                '__builder__': js_callback,
                '_attributes_': callback.attributes,
                '_constructor_': callback.constructor,
                '__default_opt__': {},
            },
        )

    def visit_callback(self, node):
        arguments = [self.visit(arg) for arg in node.arguments]
        constructor = IDLFunction(
            name='constructor',
            return_type=prepare_idl_type(node.idl_type),
            arguments=arguments,
        )

        return SimpleNamespace(
            name=node.name,
            constructor=constructor,
            attributes=arguments,
        )

    def visit_argument(self, node):
        argument_type = prepare_idl_type(node.idl_type)

        if node.optional is True:
            argument_type = IDLOptional(value=argument_type)

        return IDLArgument(name=node.name, value=argument_type)
