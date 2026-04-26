from lw_math.variable import Variable
from sympy import diff, sympify


class Expression:
    def __init__(self, value):
        if isinstance(value, Variable):
            self.sympy_expr = value.get_symbol()
            self.variable_map = {value.get_symbol(): value}

        elif isinstance(value, Expression):
            self.sympy_expr = value.sympy_expr
            self.variable_map = dict(value.variable_map)

        elif isinstance(value, (int, float, complex)):
            self.sympy_expr = sympify(value)
            self.variable_map = {}

        else:
            raise TypeError(
                f"Cannot create Expression from {type(value).__name__}"
            )

    def evaluate(self):
        substitutions = {
            symbol: variable.get_value()
            for symbol, variable in self.variable_map.items()
        }
        return self.sympy_expr.subs(substitutions)

    def __add__(self, other):
        other = Expression(other)
        result = Expression(self.sympy_expr + other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __sub__(self, other):
        other = Expression(other)
        result = Expression(self.sympy_expr - other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __truediv__(self, other):
        other = Expression(other)
        result = Expression(self.sympy_expr / other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __mul__(self, other):
        other = Expression(other)
        result = Expression(self.sympy_expr * other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __pow__(self, other):
        other = Expression(other)
        result = Expression(self.sympy_expr**other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def derivative(self, symbol):
        result = Expression(diff(self.sympy_expr, symbol))
        result.variable_map = dict(self.variable_map)
        return result

    def __str__(self):
        return str(self.sympy_expr)

    def __repr__(self):
        return f"Expression({repr(self.sympy_expr)})"

def linearize_expression(expr, variable):
    """Linearize the expression around the current value of the variable."""
    pass