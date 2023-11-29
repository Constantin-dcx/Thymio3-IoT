import M5
import math
import random
import time


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
WHITE = 0xffffff
BLACK = 0x000000

# Global variables
t = 0
current_x = WIDTH // 2
current_y = HEIGHT // 2
canvas = None


def setup():
    global eye_left, eye_right, pupil_left, pupil_right, canvas

    M5.begin()

    canvas = M5.Display.newCanvas(WIDTH, HEIGHT, 1, 1)


def draw_eyes(x, y):
    global canvas

    # Draw eyes
    x_left = x - EYE_DISTANCE // 2
    x_right = x + EYE_DISTANCE // 2
    canvas.fillCircle(x_left, y, EYE_RADIUS, WHITE)
    canvas.fillCircle(x_right, y, EYE_RADIUS, WHITE)
    
    # Draw pupils
    x_p = int( (x - WIDTH // 2) / MAX_WIDTH * EYE_RADIUS )
    y_p = int( (y - HEIGHT // 2) / MAX_HEIGHT * EYE_RADIUS )
    canvas.fillCircle(x_left + x_p, y + y_p, PUPIL_RADIUS, BLACK)
    canvas.fillCircle(x_right + x_p, y + y_p, PUPIL_RADIUS, BLACK)

    # Update canvas
    canvas.push(0, 0)

    # Erase stuff
    canvas.clear()
    # canvas.fillCircle(x_left, y, EYE_RADIUS, BLACK)
    # canvas.fillCircle(x_right, y, EYE_RADIUS, BLACK)

    # time.sleep(0.1)

def track_object():
    # global t

    # f = 0.02
    # x = (1 + math.cos(2 * math.pi * t * f)) * CAMERA_WIDTH // 2
    # y = (1 + math.sin(2 * math.pi * t * f)) * CAMERA_HEIGHT // 2
    # t = t + 1

    x = int(random.random() * CAMERA_WIDTH)
    y = int(random.random() * CAMERA_HEIGHT)

    # print(f"Object found at ({x}, {y})!")
    return x, y


def compute_eyes_position(x, y):
    x = int(EYE_DISTANCE // 2 + EYE_RADIUS + x * MAX_WIDTH / CAMERA_WIDTH)
    y = int(EYE_RADIUS + y * MAX_HEIGHT / CAMERA_HEIGHT)

    # print(f"Goal position: ({x}, {y})!")
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
    M5.update()

    # Get the object coordinates
    object_x, object_y = track_object()
    eye_x, eye_y = compute_eyes_position(object_x, object_y)
    
    # Update the eyes
    update_position(eye_x, eye_y)


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    from utility import print_error_msg
    print_error_msg(e)

    if canvas:
       canvas.delete()
