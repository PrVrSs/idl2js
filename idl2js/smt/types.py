"""Map WebIDL types to Z3 variables with range constraints."""

from z3 import And, Bool, Int, Or, Real

from idl2js.idl.std.constants import FLOAT_RANGES, INT_RANGES


def idl_type_to_z3(type_name, var_name):
    """Create a Z3 variable constrained to the IDL type's value range.

    Returns:
        (z3_var, constraint) tuple. The constraint encodes the valid range
        for the IDL type. Returns (None, None) for unsupported types.
    """
    if type_name in INT_RANGES:
        lo, hi = INT_RANGES[type_name]
        var = Int(var_name)
        return var, And(var >= lo, var <= hi)

    if type_name in FLOAT_RANGES:
        lo, hi = FLOAT_RANGES[type_name]
        var = Real(var_name)
        return var, And(var >= lo, var <= hi)

    if type_name == 'boolean':
        var = Bool(var_name)
        return var, True  # no additional constraint

    return None, None


def z3_value_to_python(z3_val):
    """Convert a Z3 model value to a Python int or float."""
    import z3

    if z3_val is None:
        return 0
    if z3.is_int_value(z3_val):
        return z3_val.as_long()
    if z3.is_rational_value(z3_val):
        frac = z3_val.as_fraction()
        return float(frac.numerator) / float(frac.denominator)
    if z3.is_algebraic_value(z3_val):
        return float(z3_val.as_decimal(20).rstrip('?'))
    # Fallback: try string conversion.
    try:
        return int(str(z3_val))
    except ValueError:
        return float(str(z3_val))
