import logging
import random
from collections import defaultdict, deque

from .exceptions import UnknownType


logger = logging.getLogger(__name__)


class TypeTable(dict):
    def __setitem__(self, key, value):
        if key in self:
            logger.debug('overload type %s', key)

        dict.__setitem__(self, key, value)


class SSA:
    pass


class CallGraph:
    pass


class SymbolTable:
    pass


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

    def add_type(self, name, value):
        self._type_table[name] = value

    def get_type(self, name):
        try:
            return self._type_table[name]
        except KeyError:
            raise UnknownType(f'Not found type {name=}') from None

    def get_random_type(self):
        return random.choice(list(self._type_table.values()))

    def add_instance(self, name, instance):
        self._instance_table[name] = instance
