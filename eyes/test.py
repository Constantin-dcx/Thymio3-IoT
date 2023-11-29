import pygame
import random
import sys
import math

# Resolution
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
WIDTH, HEIGHT = 320, 240
FPS = 15

# Smoothing
THRESHOLD = 5
SMOOTH = 0.3

# Eye parameters
EYE_RADIUS = HEIGHT // 5
PUPIL_RADIUS = EYE_RADIUS // 3
EYE_DISTANCE = EYE_RADIUS * 3

MAX_WIDTH = WIDTH - EYE_DISTANCE - EYE_RADIUS * 2
MAX_HEIGHT = HEIGHT - EYE_RADIUS * 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Global variables
t = 0
screen = None
clock = None
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
    global screen, clock

    screen.fill(BLACK)  # Fill the screen with black
    
    # Draw eyes
    x_left = x - EYE_DISTANCE // 2
    x_right = x + EYE_DISTANCE // 2
    pygame.draw.circle(screen, WHITE, (x_left, y), EYE_RADIUS)
    pygame.draw.circle(screen, WHITE, (x_right, y), EYE_RADIUS)
    
    # Draw pupils
    x_p = (x - WIDTH // 2) / MAX_WIDTH * EYE_RADIUS
    y_p = (y - HEIGHT // 2) / MAX_HEIGHT * EYE_RADIUS
    pygame.draw.circle(screen, BLACK, (x_left + x_p, y + y_p), PUPIL_RADIUS)
    pygame.draw.circle(screen, BLACK, (x_right + x_p, y + y_p), PUPIL_RADIUS)
    
    pygame.display.flip()
    clock.tick(FPS)

def track_object():
    # global t

    # f = 0.02
    # x = (1 + math.cos(2 * math.pi * t * f)) * CAMERA_WIDTH // 2
    # y = (1 + math.sin(2 * math.pi * t * f)) * CAMERA_HEIGHT // 2
    # t = t + 1

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
    global current_x, current_y

    dx, dy = THRESHOLD + 1, THRESHOLD + 1
    while norm(dx, dy) > THRESHOLD:
        dx = x - current_x
        dy = y - current_y
        current_x += int(dx * SMOOTH)
        current_y += int(dy * SMOOTH)
        
        draw_eyes(current_x, current_y)

def norm(x, y):
    return math.sqrt(x**2 + y**2)

def loop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Get the object coordinates 
    object_x, object_y = track_object()
    eye_x, eye_y = compute_eyes_position(object_x, object_y)
    
    # Update the eyes based on the object coordinates
    update_position(eye_x, eye_y)


if __name__ == "__main__":
    setup()
    while True:
        loop()

