import pygame
from object.point import distance 
from object.point import Point
import clock

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
    point_speed_px_per_s = error / 2   # speed in pixels per second
    seconds_since_last_frame = clock.DELTA_TIME 

    if error > tolerance:
        if actual_distance > demanded_distance:
            # point1.x += p1_to_p2_vector.x * (error / 2) 
            point1.x += p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point1.y += p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
            point2.x -= p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point2.y -= p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
        else:
            point1.x -= p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point1.y -= p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame
            point2.x += p1_to_p2_vector_normalized.x * point_speed_px_per_s * seconds_since_last_frame
            point2.y += p1_to_p2_vector_normalized.y * point_speed_px_per_s * seconds_since_last_frame