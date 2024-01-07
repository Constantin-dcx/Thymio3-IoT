import json
import machine
import math
import M5
import random
import time
from config import *
from umqtt.simple import MQTTClient


# Resolution
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
WIDTH, HEIGHT = 320, 240

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

# UART
PROTOCOL_START = b'{'[0]

# Detection thresholds
PERSON_THRESHOLD = 0.9
FACE_THRESHOLD = 0.9
DETECTION_TIMEOUT_MS = 500

# Global variables
t = 0
current_x = WIDTH // 2
current_y = HEIGHT // 2
canvas = None
uart = None
client = None
last_time = 0
detection_status = 'not_found'


def setup():
    global canvas, uart, client

    M5.begin()

    # Connect to MQTT
    client = MQTTClient(TRACKING_REMOTE_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    print(f'Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...')
    client.connect()
    print('Successfully connected to MQTT broker !')

    canvas = M5.Display.newCanvas(WIDTH, HEIGHT, 1, 1)
    draw_eyes(WIDTH//2, HEIGHT//2)

    # Start serial communication
    uart = machine.UART(1, tx=32, rx=33) # PORT A
    # uart = machine.UART(1, tx=14, rx=13) # PORT C
    uart.init(115200, bits=8, parity=None, stop=1)


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

def could_not_find_object():
    global t

    f = 0.02
    x = (1 + math.cos(2 * math.pi * t * f)) * CAMERA_WIDTH // 2
    y = (1 + math.sin(2 * math.pi * t * f)) * CAMERA_HEIGHT // 2
    t = t + 1

    # # Random
    # x = int(random.random() * CAMERA_WIDTH)
    # y = int(random.random() * CAMERA_HEIGHT)

    # print(f"Object found at ({x}, {y})!")
    return compute_eyes_position(x, y)


def compute_eyes_position(x, y):
    x = int(EYE_DISTANCE // 2 + EYE_RADIUS + x * MAX_WIDTH / CAMERA_WIDTH)
    y = int(EYE_RADIUS + y * MAX_HEIGHT / CAMERA_HEIGHT)

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


class Rectangle:
    def __init__(self, person: dict) -> None:
        self.w = person["w"]
        self.h = person["h"]
        self.x = CAMERA_WIDTH - int(person["x"] + 0.5*self.w)
        self.y = int(person["y"] + 0.5*self.h)


def find_best_person(persons_list: list):
    best_person = persons_list[0]

    if len(persons_list) == 1:
        return best_person
     
    for person in persons_list[1:]:
        # if person["prob"] > best_person["prob"]:

        # select widest face
        if person["w"]*person["h"] > best_person["w"]*best_person["h"]:
            best_person = person

    return best_person


def compute_rectangle(result, mode: str = "Face Detector") -> Rectangle:

    try:
        # Check we are actually running the right function
        running_function = result["running"]
        if running_function != mode:
            print(f"ERROR: UnitV2 is running '{running_function}'. Expected '{mode}'.")
            return
        
        if mode == "Object Recognition":
            # Get the persons found in the image
            persons_found = list()
            for object in result["obj"]:
                if object["type"] == "person" and object["prob"] > PERSON_THRESHOLD:
                    persons_found.append(object)
            
            if not persons_found:
                return
            
            best_object = find_best_person(persons_found)
        
        elif mode == "Face Detector":
            # Get the faces found in the image
            faces_found = list()
            for object in result["face"]:
                if object["prob"] > FACE_THRESHOLD:
                    faces_found.append(object)

            if not faces_found:
                return
        
            best_object = find_best_person(faces_found)

        return Rectangle(best_object)
    
    except KeyError as err:
        print(f"ERROR: Could not parse results:\n{result} \nKeyError: {err}.")


def track_object() -> Rectangle:
    global uart, detection_status

    # Read UnitV2 serial data    
    if not uart.any():
        return

    data = uart.readline()
    if data is None or data[0] != PROTOCOL_START:
        return

    # Decode json data
    try:
        result = json.loads(data)
    except ValueError as err:
        print(f'WARNING: Could not decode json data: \n{data}')
        return

    detection_status = 'found'

    return compute_rectangle(result)


def loop():
    global client, last_time, detection_status
    M5.update()

    # Get the object coordinates
    rect = track_object()

    if rect is None:
        # If no result received in DETECTION_TIMEOUT_MS, stop moving
        if time.ticks_diff(time.ticks_ms(), last_time) > DETECTION_TIMEOUT_MS:
            client.publish(CAMERA_DETECT_TOPIC, FACE_NOT_FOUND)
            last_time = time.ticks_ms()
            detection_status = 'not_found'

        if detection_status == 'not_found':
            # Draw 'lost' eyes
            update_position(*could_not_find_object())

        return
    
    last_time = time.ticks_ms()

    message = {"x": rect.x, "y": rect.y, "w": rect.w, "h": rect.h}
    msg_json = json.dumps(message)
    client.publish(CAMERA_DETECT_TOPIC, msg_json)
    
    eye_x, eye_y = compute_eyes_position(rect.x, rect.y)
    
    # Update the eyes
    update_position(eye_x, eye_y)
    # draw_eyes(eye_x, eye_y)


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
