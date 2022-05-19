class TranspilerException(Exception):
    pass


class IDLParseError(TranspilerException):
    pass


class RuntimeException(TranspilerException):
    pass


class UnknownType(TranspilerException):
    pass
