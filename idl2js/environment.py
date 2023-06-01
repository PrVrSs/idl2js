import logging
from collections import defaultdict, deque

from .exceptions import UnknownType


logger = logging.getLogger(__name__)


class TypeTable(dict):
    def __setitem__(self, key, value):
        if key in self:
            logger.debug('overload type %s', key)

        dict.__setitem__(self, key, value)


class DependencyNode:
    def __init__(self, value):
        self.value = value

        self._children = []

    def append(self, node):
        self._children.append(node)

    def __str__(self):
        return f'{self.value} -> [{", ".join([str(i) for i in self._children])}]'


def build_dependency_graph(idl_type, environment):
    root = DependencyNode(idl_type.__type__)

    todo = deque([(idl_type, root)])
    while todo:
        item, node = todo.popleft()

        deps = item.dependencies()
        for dep in deps:
            new_type = environment.get_type(dep)
            new_node = DependencyNode(new_type.__type__)
            node.append(new_node)
            todo.append((new_type, new_node))

    return root

class IRTable:
    def __init__(self):
        self._queue = deque()


class InstanceTable:
    def __init__(self):
        self._instances = defaultdict(list)

    def __setitem__(self, key, value):
        self._instances[key].append(value)

    def __getitem__(self, item):
        return self._instances[item]


class Environment:
    def __init__(self, idl_type):
        self._type_table = TypeTable(idl_type)
        self._ir_table = IRTable()
        self._instance_table = InstanceTable()
        self._dependency_graph = self._create_dependency_graph()

    def add_type(self, name, value):
        self._type_table[name] = value
        self._dependency_graph[name] = build_dependency_graph(value, self)

    def get_dependency_graph(self, idl_type):
        return self._dependency_graph[idl_type]

    def get_type(self, name):
        try:
            return self._type_table[name]
        except KeyError:
            raise UnknownType(f'Not found type {name=}') from None

    def add_instance(self, name, instance):
        self._instance_table[name] = instance

    def _create_dependency_graph(self):
        return {
            key: build_dependency_graph(value, self)
            for key, value in self._type_table.items()
        }
