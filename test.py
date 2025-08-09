import pygame
import sys

# from cosntraint.constraint import distance_constraint 
# from cosntraint.constraint import associate_constraint
from cosntraint.constraint import associate_constraint, distance_constraint
from object.point import Point, distance 
import clock

pygame.init()
SIMULATION_TO_REAL_TIME_CHANGE_RATIO = 1

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pointRed = Point(300, 300)
pointBlue = Point(0, 400)
pointGreen = Point(500, 22)
pointBlack = Point(900, 400)

# Initialize with triangle at center
# center = [WIDTH / 2, HEIGHT / 2]

# initialize objects and constraints
# Main loop
running = True
while running:  
    clock.DELTA_TIME = clock.clock.tick(60) / 1000

    mouse_x, mouse_y = pygame.mouse.get_pos()
    # print(f"Mouse position: {mouse_x}, {mouse_y}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(pointRed.x), int(pointRed.y)), pointRed.radius)
    pygame.draw.circle(screen, (0, 0, 255), (int(pointBlue.x), int(pointBlue.y)), pointBlue.radius)
    pygame.draw.circle(screen, (0, 255, 0), (int(pointGreen.x), int(pointGreen.y)), pointGreen.radius)
    # pygame.draw.circle(screen, (0, 0, 0), (int(pointBlack.x), int(pointBlack.y)), pointBlack.radius)

    # time.sleep(2)  # Simulate some processing time
    associate_constraint(distance_constraint, pointRed, pointBlue, 30)
    associate_constraint(distance_constraint, pointRed, pointGreen, 30)
    associate_constraint(distance_constraint, pointBlue, pointGreen, 30)
    # print(f"distance between red and blue: {distance(pointRed, pointBlue)}")
    # print(f"distance between red and green: {distance(pointRed, pointGreen)}")
    # associate_constraint(distance_constraint, pointBlack, pointGreen, 30)
    # associate_constraint(distance_constraint, pointBlack, pointBlue, 200)
    # print(f"distance between black and blue: {distance(pointBlack, pointBlue)}")
    # print(f"distance between black and green: {distance(pointBlack, pointGreen)}")
    # execute_constraints()  # Update constraints if needed
    pygame.display.flip() 

pygame.quit()
sys.exit()
