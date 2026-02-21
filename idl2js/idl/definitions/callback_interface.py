from idl2js.builders.js import js_interface

from .definition import Interface
from .interface import InterfaceVisitor


class CallbackInterfaceVisitor(InterfaceVisitor):
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
                '_inheritance_': getattr(interface, 'inheritance', None),
                '__default_opt__': {},
            },
        )
