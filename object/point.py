class Point:
    def __init__(self, x, y, isFixed=False, isPhantom=False, radius=6):
        self._x = x
        self._y = y
        self._radius = radius
        self._isFixed = isFixed
        self._isPhantom = isPhantom  

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        if not self._isFixed:
            self._x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        if not self._isFixed:
            self._y = value

    @property
    def radius(self):
        return self._radius
    
    @radius.setter 
    def radius(self, value):
        self._radius = value

    @property
    def isFixed(self):
        return self._isFixed
    
    @isFixed.setter
    def isFixed(self, value):
        self._isFixed = value

    def fix(self, x, y):
        """Set the fixed state of the point."""
        self._isFixed = True
        self._x = x
        self._y = y 
    
    def unfix(self):
        """Set the point to be movable."""
        self._isFixed = False
        
    @property
    def isPhantom(self):
        return self._isPhantom
    
    @isPhantom.setter
    def isPhantom(self, value):
        self._isPhantom = value

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

def distance(point1: Point, point2: Point) -> float:
    """Calculate the distance between two points."""
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5