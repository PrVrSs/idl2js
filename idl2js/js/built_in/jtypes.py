type_class_dict = {}


class PrimitiveType:
    def __init__(self, builder):
        self._builder = builder

    def __init_subclass__(cls, name: str, **kwargs):
        type_class_dict[name] = cls

    def build(self):
        return self._builder.build(self)
