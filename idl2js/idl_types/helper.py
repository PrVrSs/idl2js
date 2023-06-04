def get_base_type(idl_type):
    while True:
        if isinstance(idl_type, IDLType):
            return idl_type.value

        idl_type = idl_type.unwrap()


class IDLFunction:
    def __init__(self, name, return_type, arguments=None):
        self.name = name
        self.arguments = arguments or []
        self.return_type = return_type

    def __repr__(self):
        return f'{self.name}({self.arguments})'


class IDLArgument:
    def __init__(self, name, value, const=None):
        self.name = name
        self.value = value
        self.const = const

    def unwrap(self):
        return self.value

    def __repr__(self):
        return f'{self.name}: {self.value}'


class IDLOptional:
    def __init__(self, value):
        self.value = value

    def unwrap(self):
        return self.value

    def __repr__(self):
        return f'FOptional[{self.value}]'


class IDLProperty:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name}: {self.value}'

class IDLType:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value


class IDLUnion:
    def __init__(self, items):
        self.items = items


class IDLSequence:
    def __init__(self, items):
        self.items = items

    @property
    def result(self):
        return self.items

    def __repr__(self):
        return f'FSequence[{self.items[0]}]'
