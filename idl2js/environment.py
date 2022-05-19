import logging
from collections import defaultdict, deque

from .exceptions import UnknownType


logger = logging.getLogger(__name__)


class TypeTable(dict):
    def __setitem__(self, key, value):
        if key in self:
            logger.debug('overload type %s', key)

        dict.__setitem__(self, key, value)


class InstanceTable:
    def __init__(self):
        self._queue = deque()
        self._instances = defaultdict(list)

    @property
    def instances(self):
        return list(self._queue)

    def __setitem__(self, key, value):
        self._queue.append(value)
        self._instances[key].append(value)

    def __getitem__(self, item):
        return self._instances[item]


class Environment:
    def __init__(self):
        self._type_table = TypeTable()
        self._instances = InstanceTable()

    def add_type(self, name, value):
        self._type_table[name] = value

    def get_type(self, name):
        try:
            return self._type_table[name]
        except KeyError:
            raise UnknownType(f'Not found type {name=}') from None

    def add_instance(self, name, instance):
        self._instances[name] = instance

    def get_variable(self):
        return self._instances.instances
