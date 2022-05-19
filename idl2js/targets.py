class MetaTarget(type):
    def __new__(mcs, typename, bases, ns):
        return super().__new__(mcs, typename, bases, ns)


class BaseTarget(metaclass=MetaTarget):
    strategy = None
    kind = None
    fields = None
    counts = None


class InterfaceTarget(BaseTarget):
    kind = 'unknown'
    counts = 0
