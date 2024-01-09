import json
import M5
import time
from config import *
from eyes import Eyes
from umqtt.simple import MQTTClient
from unitV2 import UnitV2


# Detection thresholds
PERSON_THRESHOLD = 0.9
FACE_THRESHOLD = 0.9
DETECTION_TIMEOUT_MS = 500

# Resolution
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240


class DetectionStatus:
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"

class Rectangle:
    def __init__(self, person: dict) -> None:
        self.w = person["w"]
        self.h = person["h"]
        self.x = CAMERA_WIDTH - int(person["x"] + 0.5*self.w)
        self.y = int(person["y"] + 0.5*self.h)


# Global variables
eyes = None
unitV2 = None
client = None
last_time = 0
detection_status = DetectionStatus.NOT_FOUND
update_unitv2_ip = False


def setup():
    global eyes, unitV2, client

    M5.begin()

    # Initialize Eyes display
    eyes = Eyes(screen_width = SCREEN_WIDTH, screen_height = SCREEN_HEIGHT, 
                camera_width = CAMERA_WIDTH, camera_height = CAMERA_HEIGHT)

    # Initialize UnitV2 communication
    unitV2 = UnitV2(tx=32, rx=33)  # PORT A
    # unitV2 = UnitV2(tx=14, rx=13)  # PORT C with DIN Base

    # Connect to MQTT
    client = MQTTClient(TRACKING_ON_BOARD_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.set_callback(mqtt_callback)
    print(f'Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...')
    client.connect()
    print('Successfully connected to MQTT broker !')
    client.subscribe(CAMERA_IP_GET_TOPIC)


def mqtt_callback(topic, msg):
    global unitV2

    topic_str = topic.decode()
    
    if topic_str == CAMERA_IP_GET_TOPIC:
        unitV2.get_ip()


def find_best_person(persons_list: list):
    best_person = persons_list[0]

    if len(persons_list) == 1:
        return best_person
     
    for person in persons_list[1:]:
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
        
        # Not so good
        if mode == "Object Recognition":
            # Get the persons found in the image with probability > PERSON_THRESHOLD
            persons_found = list()
            for object in result["obj"]:
                if object["type"] == "person" and object["prob"] > PERSON_THRESHOLD:
                    persons_found.append(object)
            
            if not persons_found:
                return
            
            best_object = find_best_person(persons_found)
        
        elif mode == "Face Detector":            
            faces_found = result["face"]
            best_object = find_best_person(faces_found)

        return Rectangle(best_object)
    
    except KeyError as err:
        print(f"ERROR: Could not parse results:\n{result} \nKeyError: {err}.")


def loop():
    global client, last_time, detection_status, eyes
    M5.update()
    client.check_msg()

    rect = None

    # Receive data from UnitV2
    data = unitV2.read_serial()

    if data is not None:

        if "ip" in data:
            # Communicate UnitV2 ip to remote Core2
            ip_address = data["ip"]
            print(f"UnitV2 IP adress: '{ip_address}'")
            client.publish(CAMERA_IP_POST_TOPIC, ip_address)

        if "running" in data:
            rect = compute_rectangle(data)

    if rect is None:
        # If no result received in DETECTION_TIMEOUT_MS, stop Thymio3
        if time.ticks_diff(time.ticks_ms(), last_time) > DETECTION_TIMEOUT_MS:
            client.publish(CAMERA_DETECT_TOPIC, FACE_NOT_FOUND)
            last_time = time.ticks_ms()
            detection_status = DetectionStatus.NOT_FOUND

        # Draw 'lost' eyes
        if detection_status == DetectionStatus.NOT_FOUND:
            eyes.could_not_find_object()

        return
    
    last_time = time.ticks_ms()
    detection_status = DetectionStatus.FOUND

    # Send rectangle coordinates to Thymio3
    message = {"x": rect.x, "y": rect.y, "w": rect.w, "h": rect.h}
    msg_json = json.dumps(message)
    client.publish(CAMERA_DETECT_TOPIC, msg_json)
    
    # Update the eyes
    eyes.go_to(cam_x=rect.x, cam_y=rect.y)


if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        from utility import print_error_msg
        print_error_msg(e)

        eyes.delete_canvas()
