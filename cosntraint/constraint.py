import pygame
import clock
from typing import Optional
from object.point import distance, Point 
from object.segment import Segment

def associate_constraint(constraint, *objects):
    """Associate  constraint with objects."""
    constraint(*objects)
    
def distance_constraint(point1: Point, 
                        point2: Point, 
                        demanded_distance, 
                        tolerance=2): # distance in pixel values
    """Ensure the distance between two points is equal to a specified value."""

    actual_distance = distance(point1, point2)
    error = abs(actual_distance - demanded_distance)

    p1_to_p2_vector = pygame.math.Vector2(point2.x - point1.x, point2.y - point1.y)
    p1_to_p2_vector_normalized = p1_to_p2_vector.normalize() 
    point_speed_px_per_s = error + 200 # TODO: find flexible way to set the speed
    seconds_since_last_frame = clock.DELTA_TIME_IN_SECONDS 

    if error > tolerance:
        if actual_distance > demanded_distance:
            point1.x += p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point1.y += p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
            point2.x -= p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point2.y -= p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
        else:
            point1.x -= p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point1.y -= p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
            point2.x += p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point2.y += p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame

# TODO: Important!!! fix a point with respect to a specific axis
def fix_point_constraint(point: Point, fixed_phantom_point: Optional[Point] = None):
    """Fix a point at a specific position."""

    if fixed_phantom_point is not None and fixed_phantom_point.isPhantom:
        point.x = fixed_phantom_point.x
        point.y = fixed_phantom_point.y

    point.isFixed = True


def angle_between_segments_constraint(segment1: Segment, 
                                      segment2: Segment,
                                       angleDegree: float, 
                                                tolerance=2):
    """Keep the segment at a specific angle with respect to the horizon. Angle is in degrees."""
    

    
def fix_segment_constraint(segment: Segment, 
                                    fixed_start_x: float, 
                                    fixed_start_y: float, 
                                    fixed_end_x: float, 
                                    fixed_end_y: float, 
                                    tolerance=2):
    """Fix a segment at a specific position."""
    
    # the reason for not having a Segment object here is that 
    # each new segment created is added to the set of live objects
    pass