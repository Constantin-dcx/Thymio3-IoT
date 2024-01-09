import math
import M5
import random


# Helper functions
def norm(x, y):
    return math.sqrt(x**2 + y**2)

def sign(x):
    return (x > 0) - (x < 0)


class Eyes:
    # Smoothing parameters
    EYE_THRESHOLD = 5
    EYE_SMOOTH = 0.3
    EYE_MAX_SPEED = 10

    # Colors
    WHITE = 0xffffff
    BLACK = 0x000000

    def __init__(self, screen_width: int = 320, screen_height: int = 240, 
                 camera_width: int = 640, camera_height: int = 480) -> None:
        
        # Resolution
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.CAMERA_WIDTH = camera_width
        self.CAMERA_HEIGHT = camera_height

        # Eye parameters
        self.EYE_RADIUS = self.SCREEN_HEIGHT // 5
        self.PUPIL_RADIUS = self.EYE_RADIUS // 3
        self.EYE_DISTANCE = self.EYE_RADIUS * 3
        self.MAX_WIDTH = self.SCREEN_WIDTH - self.EYE_DISTANCE - self.EYE_RADIUS * 2
        self.MAX_HEIGHT = self.SCREEN_HEIGHT - self.EYE_RADIUS * 2

        # Initialize variables
        self.t = 0
        self.current_x = self.SCREEN_WIDTH // 2
        self.current_y = self.SCREEN_HEIGHT // 2

        # Start screen
        self.canvas = M5.Display.newCanvas(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 1, 1)
        self._draw(self.current_x, self.current_y)

    def could_not_find_object(self, circle = True):

        if circle:
            f = 0.02
            x = (1 + math.cos(2 * math.pi * self.t * f)) * self.CAMERA_WIDTH // 2
            y = (1 + math.sin(2 * math.pi * self.t * f)) * self.CAMERA_HEIGHT // 2
            self.t = self.t + 1

        else:
            x = int(random.random() * self.CAMERA_WIDTH)
            y = int(random.random() * self.CAMERA_HEIGHT)

        self.go_to(x, y)

    def go_to(self, cam_x, cam_y):

        x, y = self._camera_to_eyes_position(cam_x, cam_y)

        dx, dy = self.EYE_THRESHOLD + 1, self.EYE_THRESHOLD + 1
        while norm(dx, dy) > self.EYE_THRESHOLD:
            dx = x - self.current_x
            dy = y - self.current_y
            speed_x = int(dx * self.EYE_SMOOTH)
            speed_y = int(dy * self.EYE_SMOOTH)
            self.current_x += sign(speed_x) * min(abs(speed_x), self.EYE_MAX_SPEED)
            self.current_y += sign(speed_y) * min(abs(speed_y), self.EYE_MAX_SPEED)

            self._draw(self.current_x, self.current_y)
    
    def delete_canvas(self):
        if self.canvas:
            self.canvas.delete()

    def _camera_to_eyes_position(self, x, y):
        x = int(self.EYE_DISTANCE // 2 + self.EYE_RADIUS + x * self.MAX_WIDTH / self.CAMERA_WIDTH)
        y = int(self.EYE_RADIUS + y * self.MAX_HEIGHT / self.CAMERA_HEIGHT)

        return x, y

    def _draw(self, x, y):

        # Draw eyes
        x_left = x - self.EYE_DISTANCE // 2
        x_right = x + self.EYE_DISTANCE // 2
        self.canvas.fillCircle(x_left, y, self.EYE_RADIUS, self.WHITE)
        self.canvas.fillCircle(x_right, y, self.EYE_RADIUS, self.WHITE)
        
        # Draw pupils
        x_p = int( (x - self.SCREEN_WIDTH // 2) / self.MAX_WIDTH * self.EYE_RADIUS )
        y_p = int( (y - self.SCREEN_HEIGHT // 2) / self.MAX_HEIGHT * self.EYE_RADIUS )
        self.canvas.fillCircle(x_left + x_p, y + y_p, self.PUPIL_RADIUS, self.BLACK)
        self.canvas.fillCircle(x_right + x_p, y + y_p, self.PUPIL_RADIUS, self.BLACK)

        # Update canvas
        self.canvas.push(0, 0)
        self.canvas.clear()
