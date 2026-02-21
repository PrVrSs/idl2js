from types import SimpleNamespace

from pywebidl2.expr import Ast as WebIDLAst

from idl2js.builders.js import js_dictionary
from idl2js.visitor import Visitor

from .definition import Dictionary
from .helper import IDLArgument, prepare_idl_type
from .interface import extract_default


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
                '_inheritance_': dictionary.inheritance,
                '__default_opt__': {},
                '__generator__': lambda: None,
            },
        )

    def visit_dictionary(self, node):
        return SimpleNamespace(
            name=node.name,
            inheritance=getattr(node, 'inheritance', None),
            attributes=[self.visit(member) for member in node.members],
        )

    def visit_field(self, node):
        return IDLArgument(
            name=node.name,
            value=prepare_idl_type(node.idl_type),
            default=extract_default(getattr(node, 'default', None)),
        )
