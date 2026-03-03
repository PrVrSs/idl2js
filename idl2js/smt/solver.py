from z3 import Or, Solver, sat

from idl2js.smt.predicates import OraclePredicate
from idl2js.smt.types import idl_type_to_z3, z3_value_to_python


class SMTSolver:
    """Solve oracle predicates and produce concrete satisfying values."""

    def __init__(self, predicate: OraclePredicate):
        self._predicate = predicate

    def solve(self, extra_constraints=None):
        """Find a satisfying assignment for the oracle predicate.

        Returns:
            dict mapping field names to concrete Python values, or None if unsat.
        """
        solver = Solver()
        z3_vars = {}

        for field_name, idl_type in self._predicate.fields.items():
            var, constraint = idl_type_to_z3(idl_type, field_name)
            if var is None:
                continue
            z3_vars[field_name] = var
            if constraint is not True:
                solver.add(constraint)

        solver.add(self._predicate.formula_fn(z3_vars))

        if extra_constraints:
            for c in extra_constraints:
                solver.add(c)

        if solver.check() == sat:
            model = solver.model()
            return {
                name: z3_value_to_python(model.eval(var, model_completion=True))
                for name, var in z3_vars.items()
            }
        return None

    def solve_many(self, count=10, extra_constraints=None):
        """Generate multiple distinct solutions using blocking clauses.

        Each solution is blocked after being found, so subsequent solutions
        must differ in at least one variable.

        Returns:
            list of dicts, each mapping field names to concrete Python values.
        """
        solver = Solver()
        z3_vars = {}

        for field_name, idl_type in self._predicate.fields.items():
            var, constraint = idl_type_to_z3(idl_type, field_name)
            if var is None:
                continue
            z3_vars[field_name] = var
            if constraint is not True:
                solver.add(constraint)

        solver.add(self._predicate.formula_fn(z3_vars))

        if extra_constraints:
            for c in extra_constraints:
                solver.add(c)

        solutions = []
        for _ in range(count):
            if solver.check() != sat:
                break

            model = solver.model()
            solution = {
                name: z3_value_to_python(model.eval(var, model_completion=True))
                for name, var in z3_vars.items()
            }
            solutions.append(solution)

            # Block this exact solution so the next one must differ.
            block = Or(*[var != model.eval(var, model_completion=True)
                         for var in z3_vars.values()])
            solver.add(block)

        return solutions
