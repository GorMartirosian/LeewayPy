from scipy.optimize import least_squares
from object.point import Point
from object.segment import Segment
from constraint.ConstraintEntry import ConstraintEntry
from lw_math.expression import Expression
from sympy import sqrt

CONSTRAINTS = []


def associate_constraint(constraint, *objects):
    """Associate  constraint with objects."""
    CONSTRAINTS.append(ConstraintEntry(constraint, objects))


def get_distance_error_expression(objects):
    point1, point2, demanded_distance = objects
    # Create variables for point coordinates
    p1x = Expression(point1.get_x_variable())
    p1y = Expression(point1.get_y_variable())
    p2x = Expression(point2.get_x_variable())
    p2y = Expression(point2.get_y_variable())
    demanded_dist = Expression(demanded_distance)

    error_expr = ((p1x - p2x) ** 2 + (p1y - p2y) ** 2) ** 0.5 - demanded_dist

    return error_expr


def distance_constraint(point1: Point, point2: Point, demanded_distance):
    pass


# TODO: Important!!! fix a point with respect to a specific axis
def fix_point_constraint(point: Point, fixed_phantom_point: Optional[Point] = None):
    """Fix a point at a specific position."""
    pass


def angle_between_segments_constraint(
    segment1: Segment, segment2: Segment, angleDegree: float, tolerance=2
):
    """Keep the segment at a specific angle with respect to the horizon. Angle is in degrees."""
    pass


def perpendicular_segment_constraint(segment: Segment, point: Point, tolerance=2):
    """Keep a segment perpendicular to a point."""
    pass


def fix_segment_constraint(
    segment: Segment,
    fixed_start_x: float,
    fixed_start_y: float,
    fixed_end_x: float,
    fixed_end_y: float,
    tolerance=2,
):
    """Fix a segment at a specific position."""

    # the reason for not having a Segment object here is that
    # each new segment created is added to the set of live objects
    pass


def point_on_circle_constraint(point: Point, center: Point, radius: float, tolerance=2):
    """Keep a point on a circle with respect to a center and radius."""
    pass


def circle_length_constraint(
    circle_center: Point, radius: float, demanded_length: float, tolerance=2
):
    """Keep a circle at a specific length."""
    pass
