from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_type_def
from idl2js.generators.generator import ChoiceGenerator
from idl2js.idl_types.generic import TypeDef
from idl2js.idl_types.utils import prepare_idl_type
from idl2js.visitor import Visitor


class TypeDefVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        typedef = self.visit_typedef(node)

        return type(
            typedef.name,
            (TypeDef,),
            {
                '__type__': typedef.name,
                '__builder__': js_type_def,
                '_attributes_': typedef.attributes,
                '__default_opt__': {},
                '__generator__': ChoiceGenerator,
            },
        )

    def visit_typedef(self, node):
        return SimpleNamespace(
            name=node.name,
            attributes=prepare_idl_type(node.idl_type.idl_type)
        )
