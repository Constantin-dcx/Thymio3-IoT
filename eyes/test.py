import pygame
import random
import sys
import math

# Camera resolution
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
# Screen resolution
WIDTH, HEIGHT = 320, 240

# Smoothing
THRESHOLD = 5
SMOOTH = 5

# Eye parameters
EYE_RADIUS = HEIGHT // 8
PUPIL_RADIUS = EYE_RADIUS // 3
EYE_DISTANCE = EYE_RADIUS * 3

MAX_WIDTH = WIDTH - EYE_DISTANCE - EYE_RADIUS * 2
MAX_HEIGHT = HEIGHT - EYE_RADIUS * 2

# Global variables
screen = None
current_x = WIDTH // 2
current_y = HEIGHT // 2

def setup():
    global screen, clock
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Animated Eyes")

    clock = pygame.time.Clock()

# Function to draw an eye at the specified coordinates
def draw_eyes(x, y):
    global screen
    # print(f"Drawing eyes at ({x}, {y})")

    screen.fill((255, 255, 255))  # Fill the screen with white
    
    # Draw left eye
    pygame.draw.circle(screen, (0, 0, 0), (x - EYE_DISTANCE // 2, y), EYE_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255), (x - EYE_DISTANCE // 2, y), PUPIL_RADIUS)
    
    # Draw right eye
    pygame.draw.circle(screen, (0, 0, 0), (x + EYE_DISTANCE // 2, y), EYE_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255), (x + EYE_DISTANCE // 2, y), PUPIL_RADIUS)
    
    pygame.display.flip()

def track_object():
    x = int(random.random() * CAMERA_WIDTH)
    y = int(random.random() * CAMERA_HEIGHT)

    print(f"Object found at ({x}, {y})!")
    return x, y

def compute_eyes_position(x, y):
    x = int(EYE_DISTANCE // 2 + EYE_RADIUS + x * MAX_WIDTH / CAMERA_WIDTH)
    y = int(EYE_RADIUS + y * MAX_HEIGHT / CAMERA_HEIGHT)

    print(f"Goal position: ({x}, {y})!")
    return x, y

def update_position(x, y):
    global current_x, current_y, clock

    dx = x - current_x
    dy = y - current_y
    distance = norm(dx, dy)
    while distance > THRESHOLD:
        # print(f"{dx=}, {dy=}")
        current_x += int(dx / distance * SMOOTH)
        current_y += int(dy / distance * SMOOTH)
        
        draw_eyes(current_x, current_y)
        pygame.time.delay(10)
        clock.tick(10)

        dx = x - current_x
        dy = y - current_y
        distance = norm(dx, dy)

def norm(x, y):
    return math.sqrt(x**2 + y**2)

def loop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Update the object coordinates 
    object_x, object_y = track_object()
    eye_x, eye_y = compute_eyes_position(object_x, object_y)
    # eye_x, eye_y = compute_eyes_position(CAMERA_WIDTH, CAMERA_HEIGHT)
    
    # Update the eyes based on the object coordinates
    update_position(eye_x, eye_y)


if __name__ == "__main__":
    setup()
    while True:
        loop()

