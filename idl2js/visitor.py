from operator import attrgetter
from typing import Any, Generic, TypeVar

import stringcase
from attr import fields


AstType = TypeVar('AstType')


class Visitor(Generic[AstType]):
    def visit(self, node: AstType) -> Any:
        """Visit a node."""
        visitor = getattr(
            self,
            f'visit_{stringcase.snakecase(node.__class__.__name__)}',
            self.generic_visit,
        )

        return visitor(node)

    def generic_visit(self, node: AstType) -> None:
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
