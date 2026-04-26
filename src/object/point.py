from lw_math.variable import Variable


class Point:
    def __init__(self, x, y, isFixed=False, isPhantom=False):
        self._x = Variable(x)
        self._y = Variable(y)
        self._isFixed = isFixed
        self._isPhantom = isPhantom

    def get_x(self):
        return self._x.get_value()

    def set_x(self, value):
        if not self._isFixed:
            self._x.set_value(value)

    def get_y(self):
        return self._y.get_value()

    def set_y(self, value):
        if not self._isFixed:
            self._y.set_value(value)

    def get_x_variable(self):
        return self._x

    def get_y_variable(self):
        return self._y

    def is_fixed(self):
        return self._isFixed

    def set_is_fixed(self, value):
        self._isFixed = value

    def is_phantom(self):
        return self._isPhantom

    def set_is_phantom(self, value):
        self._isPhantom = value

    def fix(self, x, y):
        """Set the fixed state of the point."""
        self._isFixed = True
        self._x.set_value(x)
        self._y.set_value(y)

    def unfix(self):
        """Set the point to be movable."""
        self._isFixed = False

    def __repr__(self):
        return f"Point({self.get_x()}, {self.get_y()})"

    def distance(self, other: "Point") -> float:
        """Calculate the distance between this point and another point."""
        return (
            (self.get_x() - other.get_x()) ** 2 + (self.get_y() - other.get_y()) ** 2
        ) ** 0.5
