import pygame
import sys
from constraint.constraint import (
    associate_constraint,
    distance_constraint,
    fix_point_constraint,
)
from object.point import Point, distance
from object.segment import Segment
import clock
import numpy as np
from scipy.optimize import least_squares

def constraints(variables):
    x1, y1, x2, y2, x3, y3, x4, y4 = variables
    return [
        np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) - 100,
        np.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2) - 100,
        np.sqrt((x4 - x2) ** 2 + (y4 - y2) ** 2) - 100,
        np.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2) - 100,
        np.multiply((x2 - x1), (x3 - x1)) + np.multiply((y2 - y1), (y3 - y1)),  # right angle at point 1
        np.multiply((x4 - x3), (x2 - x1)) + np.multiply((y4 - y3), (y2 - y1)),  # right angle at point 1
    ]

def solve(variables):
    x1, y1, x2, y2, x3, y3, x4, y4 = variables
    X0 = np.array([x1, y1, x2, y2, x3, y3, x4, y4])
    return least_squares(constraints, X0)

pygame.init()
SIMULATION_TO_REAL_TIME_CHANGE_RATIO= 1

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

redPoint = Point(300, 300)
bluePoint = Point(0, 400)
greenPoint = Point(500, 22)
blackPoint = Point(100, 200)
redBlueSegment = Segment(redPoint, bluePoint)  # Placeholder for a segment if needed

running = True
while running:
    clock.DELTA_TIME_IN_SECONDS = clock.clock.tick(60) / 1000
    point_speed_px_per_sec = 20  

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.draw.circle(
        screen, (255, 0, 0), (int(redPoint.x), int(redPoint.y)), redPoint.radius
    )
    pygame.draw.circle(
        screen, bluePoint.color, (int(bluePoint.x), int(bluePoint.y)), bluePoint.radius
    )
    pygame.draw.circle(
        screen, greenPoint.color, (int(greenPoint.x), int(greenPoint.y)), greenPoint.radius
    )
    pygame.draw.circle(
        screen, blackPoint.color, (int(blackPoint.x), int(blackPoint.y)), blackPoint.radius
    )
    pygame.draw.line(
        screen, (0, 255, 255), (redPoint.x, redPoint.y), (bluePoint.x, bluePoint.y), 3
    )  # red line, width=3 px

    solution = solve([redPoint.x, redPoint.y, 
            bluePoint.x, bluePoint.y, 
            greenPoint.x, greenPoint.y, 
            blackPoint.x, blackPoint.y])
    
    print(solution)


    redPoint.x, redPoint.y = solution.x[0], solution.x[1]
    bluePoint.x, bluePoint.y = solution.x[2], solution.x[3]
    greenPoint.x, greenPoint.y = solution.x[4], solution.x[5]
    blackPoint.x, blackPoint.y = solution.x[6], solution.x[7]

    pygame.display.flip()
    print(f"Point Red: {redPoint}, Point Blue: {bluePoint}, Point Green: {greenPoint}")
    print(distance(redPoint, bluePoint))
    print(distance(redPoint, greenPoint))
    print(distance(bluePoint, blackPoint))
    print(distance(greenPoint, blackPoint))

pygame.quit()
sys.exit()
