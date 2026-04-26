from sympy import symbols


class Variable:
    _counter = 0

    def __init__(self, value):
        Variable._counter += 1
        self.name = f"X_{Variable._counter}"
        self.symbol = symbols(self.name)
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_symbol(self):
        return self.symbol

    def __repr__(self):
        return f"Variable({self.name}, value={self.value})"

    def __str__(self):
        return self.name