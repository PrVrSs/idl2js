class MetaTarget(type):
    def __new__(mcs, typename, bases, ns):
        return super().__new__(mcs, typename, bases, ns)


class BaseTarget(metaclass=MetaTarget):
    strategy = None
    kind = None
    fields = None
    counts = None
    constraints = []


class InterfaceTarget(BaseTarget):
    kind = 'unknown'
    counts = 0



# class Definition(BaseTarget):
#
#     kind = None
#
#     __constructor__ = [
#
#     ]
#
#     __constrains__ = [
#
#     ]
#
#     __type_constrains__ = [
#
#     ]
#
#     __dependencies__ = [
#
#     ]
#
#
# Definition(type='Module')