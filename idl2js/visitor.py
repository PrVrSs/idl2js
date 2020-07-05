from operator import attrgetter
from typing import Generic, TypeVar

import stringcase
from attr import fields


AstType = TypeVar('AstType')


class Visitor(Generic[AstType]):

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

            if isinstance(field, self.__orig_class__.__args__):
                self.visit(field)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, self.__orig_class__.__args__):
                        self.visit(item)
