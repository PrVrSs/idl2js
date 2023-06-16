from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_enum
from idl2js.generators.generator import ChoiceGenerator
from idl2js.visitor import Visitor

from .definition import Enum_
from .helper import prepare_idl_type


class EnumVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        enum_ = self.visit_enum(node)

        return type(
            enum_.name,
            (Enum_,),
            {
                '__type__': enum_.name,
                '__builder__': js_enum,
                '_attributes_': enum_.attributes,
                '__default_opt__': {},
                '__generator__': ChoiceGenerator,
            },
        )

    def visit_enum(self, node):
        return SimpleNamespace(
            name=node.name,
            attributes=prepare_idl_type([value.value for value in node.values])
        )
