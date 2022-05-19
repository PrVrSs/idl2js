class BaseFType:
    def build(self, builder):
        return builder.build(self)


class FModule(BaseFType):
    pass


class FFunction(BaseFType):
    def __init__(self, name, return_type, arguments=None, is_constructor=False):
        self.name = name
        self.arguments = arguments or []
        self.return_type = return_type
        self.is_constructor = is_constructor

    def __repr__(self):
        return f'{self.name}({self.arguments})'


class FInterface(BaseFType):
    def __init__(self, name, superclass=None, attributes=None, namespace=None):
        self.type = name
        self.superclass = superclass
        self.attributes = attributes or {}
        self.namespace = namespace

    def __repr__(self):
        attrs = ",\n".join(map(str, self.attributes.values()))
        return f'{self.type}(\n\t{attrs},\n)'

    @property
    def constructor(self) -> FFunction:
        return self.find_attribute('constructor')

    # @property
    # def namespace(self) -> FFunction:
    #     return self.find_attribute('namespace')

    def find_attribute(self, name: str):
        try:
            return self.attributes[name]
        except KeyError:
            pass

        if self.superclass is not None:
            return self.superclass.find_attribute(name)

        return


class FArgument(BaseFType):
    def __init__(self, name, value, const=None):
        self.name = name
        self.value = value
        self.const = const

    def __repr__(self):
        return f'{self.name}: {self.value}'

    def unwrap(self):
        return self.value.build()


class FOptional(BaseFType):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'FOptional[{self.value}]'

    def unwrap(self):
        return self.value.build()


class FUnion(BaseFType):
    def __init__(self, items):
        self.items = items


class FSequence(BaseFType):
    def __init__(self, items):
        self.items = items

    @property
    def result(self):
        return self.items

    def __repr__(self):
        return f'FSequence[{self.items[0]}]'


class FDictionary(BaseFType):
    def __init__(self, items):
        self.items = items


class FConst(BaseFType):
    def __init__(self, value):
        self.value = value


class FType(BaseFType):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value
