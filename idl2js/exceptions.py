class TranspilerException(Exception):
    pass


class RuntimeException(TranspilerException):
    pass


class UnknownType(TranspilerException):
    pass
