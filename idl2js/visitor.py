from operator import attrgetter

import stringcase
from attr import fields

from .nodes import AST


class Visitor:

    def visit(self, node):
        visitor = getattr(
            self,
            f'visit_{stringcase.snakecase(node.__class__.__name__)}',
            self.generic_visit,
        )

        return visitor(node)

    def generic_visit(self, node):
        for name in map(attrgetter('name'), fields(type(node))):
            field = getattr(node, name)

            if isinstance(field, AST):
                self.visit(field)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, AST):
                        self.visit(item)
