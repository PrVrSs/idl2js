from .builder import (
    create_attribute,
    create_variable,
    create_object,
    create_operation,
    unique_name,
    Builder,
)
from .visitor import AstType, Visitor
from .storage import Storage


class InterfaceTransformer(Visitor[AstType]):

    def __init__(self, storage: Storage, builder: Builder):
        self._storage = storage
        self._builder = builder

        self._type = None
        self._name = None

    def visit_interface(self, node) -> None:
        if node.partial is True:
            return

        self._type = node.name
        self._name = unique_name()

        self.generic_visit(node)

    def visit_constructor(self, node):
        self._storage.add(
            create_variable(
                type_=self._type,
                ast=create_object(name=self._name, progenitor=self._type, arguments=[]),
            )
        )

        self.generic_visit(node)

    def visit_attribute(self, node) -> None:
        self._storage.add(
            create_variable(
                type_=node.idl_type.idl_type,
                ast=create_attribute(
                    name=unique_name(),
                    progenitor=self._name,
                    method=node.name
                ),
            )
        )

        self.generic_visit(node)

    def visit_operation(self, node) -> None:
        self._storage.add(
            create_variable(
                type_=node.idl_type.idl_type,
                ast=create_operation(
                    name=unique_name(),
                    progenitor=self._name,
                    method=node.name,
                    arguments=self._builder.create_arguments(node.arguments),
                )
            )
        )

        self.generic_visit(node)


class CollectTypedef(Visitor[AstType]):

    def __init__(self, definition_storage):
        self._definition_storage = definition_storage

    def visit_typedef(self, node):
        self._definition_storage.add_typedef(
            node.name, self.visit(node.idl_type))

    def visit_idl_type(self, node):
        idl_type = node.idl_type

        if idl_type is None:
            return

        if isinstance(idl_type, str):
            return idl_type

        if isinstance(idl_type, list):
            return [self.visit(idl) for idl in idl_type]

        return self.visit(idl_type)
