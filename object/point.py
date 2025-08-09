class Point:
    def __init__(self, x, y, radius=4):
        self.x = x
        self.y = y
        self.radius = radius  # Default radius for the point

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

def distance(point1: Point, point2: Point) -> float:
    """Calculate the distance between two points."""
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5