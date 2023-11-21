class IDL2JSException(Exception):
    """Base project exception."""


class TranspilerException(IDL2JSException):
    """Transpiler exception."""


class RuntimeException(TranspilerException):
    """Runtime exception."""


class UnknownType(TranspilerException):
    """Unknown type."""


class UnknownDefinitionType(TranspilerException):
    """Unknown definition type."""
