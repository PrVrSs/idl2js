from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_dictionary
from idl2js.idl_types.generic import Dictionary
from idl2js.idl_types.helper import IDLArgument
from idl2js.idl_types.utils import prepare_idl_type
from idl2js.visitor import Visitor


class DictionaryVisitor(Visitor[WebIDLAst]):
    def run(self, node):
        dictionary = self.visit_dictionary(node)

        return type(
            dictionary.name,
            (Dictionary,),
            {
                '__type__': dictionary.name,
                '__builder__': js_dictionary,
                '_attributes_': dictionary.attributes,
                '__default_opt__': {},
                '__generator__': lambda: None,
            },
        )

    def visit_dictionary(self, node):
        return SimpleNamespace(
            name=node.name,
            attributes=[self.visit(member) for member in node.members],
        )

    def visit_field(self, node):
        return IDLArgument(
            name=node.name,
            value=prepare_idl_type(node.idl_type),
        )
