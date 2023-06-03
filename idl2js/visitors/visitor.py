from dataclasses import fields
from operator import attrgetter
from typing import Any, Generic, TypeVar

import stringcase


AstTypeT = TypeVar('AstTypeT')


class BaseVisitor:
    def visit(self, node: AstTypeT) -> Any:
        """Visit a node."""
        visitor = getattr(
            self,
            f'visit_{stringcase.snakecase(node.__class__.__name__)}',
            self.generic_visit,
        )

        return visitor(node)

    def generic_visit(self, node: AstTypeT) -> None:
        raise NotImplementedError


class Visitor(BaseVisitor, Generic[AstTypeT]):
    def generic_visit(self, node: AstTypeT) -> None:
        """Called if no explicit visitor function exists for a node."""
        ast_type = self.__orig_bases__[0].__args__  # type: ignore

        for name in map(attrgetter('name'), fields(type(node))):
            field = getattr(node, name)

            if isinstance(field, ast_type):
                self.visit(field)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, ast_type):
                        self.visit(item)


class NodeTransformer(BaseVisitor, Generic[AstTypeT]):
    def generic_visit(self, node):
        ast_type = self.__orig_bases__[0].__args__  # type: ignore

        for name in map(attrgetter('name'), fields(type(node))):
            old_value = getattr(node, name)

            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast_type):
                        value = self.visit(value)
                        if value is None:
                            continue
                        if not isinstance(value, ast_type):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast_type):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, name)
                else:
                    setattr(node, name, new_node)
        return node
