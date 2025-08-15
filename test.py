import pygame
import sys

# from cosntraint.constraint import distance_constraint 
# from cosntraint.constraint import associate_constraint
from cosntraint.constraint import associate_constraint, distance_constraint, fix_point_constraint
from object.point import Point, distance 
from object.segment import Segment
import clock

pygame.init()
SIMULATION_TO_REAL_TIME_CHANGE_RATIO = 1

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pointRed = Point(300, 300)
pointBlue = Point(0, 400)
pointGreen = Point(500, 22)
pointBlack = Point(100, 200)
redBlueSegment = Segment(pointRed,pointBlue)  # Placeholder for a segment if needed

# Initialize with triangle at center
# center = [WIDTH / 2, HEIGHT / 2]

# initialize objects and constraints
# Main loop
running = True
while running:  
    clock.DELTA_TIME_IN_SECONDS = clock.clock.tick(60) / 1000

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(pointRed.x), int(pointRed.y)), pointRed.radius)
    pygame.draw.circle(screen, (0, 0, 255), (int(pointBlue.x), int(pointBlue.y)), pointBlue.radius)
    pygame.draw.circle(screen, (0, 255, 0), (int(pointGreen.x), int(pointGreen.y)), pointGreen.radius)
    pygame.draw.circle(screen, (0, 0, 0), (int(pointBlack.x), int(pointBlack.y)), pointBlack.radius)
    pygame.draw.line(screen, (0, 255, 255), (pointRed.x, pointRed.y), (pointBlue.x, pointBlue.y) , 3)  # red line, width=3 px

    # associate_constraint(fix_point_constraint, pointRed)
    associate_constraint(distance_constraint, pointRed, pointBlue, 100)
    associate_constraint(distance_constraint, pointRed, pointGreen, 100)
    associate_constraint(distance_constraint, pointBlue, pointBlack, 100)
    associate_constraint(distance_constraint, pointGreen, pointBlack, 100)
    associate_constraint(distance_constraint, pointRed, Point(mouse_x, mouse_y, isPhantom=True), 0)
    # associate_constraint(distance_constraint, pointBlue, Point(mouse_x,mouse_y), 100)

    pygame.display.flip() 
    print(f"Point Red: {pointRed}, Point Blue: {pointBlue}, Point Green: {pointGreen}")
    # print(distance(pointRed, pointBlue))
    # print(distance(pointRed, pointGreen))
    # print(distance(pointBlue, pointBlack))
    # print(distance(pointGreen, pointBlack))

pygame.quit()
sys.exit()
