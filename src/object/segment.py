from object.point import Point

class Segment:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Segment({self.start}, {self.end})"

    def length(self):
        return self.start.distance(self.end)