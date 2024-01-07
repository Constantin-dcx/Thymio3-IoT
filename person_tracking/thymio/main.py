import json
import machine
import thymio
import time
from config import *
from umqtt.simple import MQTTClient


CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480
POS_THRESHOLD = 20  # pixels
MAX_SPEED = 750

leds_circle = [thymio.LEDS_CIRCLE(i) for i in range(8)]
leds_rgb = [thymio.LEDS_RGB(i) for i in range(4)]
motors = thymio.MOTORS()
buttons = thymio.BUTTONS()

thymio_status = "Running"


def set_motors_speed(pos_x: float, pos_y: float):
    global motors, thymio_status

    if thymio_status != "Running":
        motors.set_speed(0, 0)
        return

    front_speed, turn_speed = 0, 0

    # Y-Axis (front)
    if abs(pos_y) > POS_THRESHOLD:
        front_speed = round(pos_y / (CAMERA_HEIGHT//2) * MAX_SPEED//2)
        # print(f"{front_speed=}")

    # X-Axis (side)
    if abs(pos_x) > POS_THRESHOLD:
        turn_speed = - round(pos_x / (CAMERA_WIDTH//2) * MAX_SPEED//6)
        # print(f"{turn_speed=}")

    # Set Motors
    left_speed = int(front_speed + turn_speed)
    right_speed = int(front_speed - turn_speed)
    # print(f'Setting motors speed: {left_speed=}, {right_speed=}')
    motors.set_speed(left_speed, right_speed)


def set_leds_circle(x: float, y: float):
    global leds_circle

    led_values = [0 for _ in range(8)]
    
    # Y-Axis (front)
    if y > POS_THRESHOLD:
        led_values[4] = y
    elif y < -POS_THRESHOLD:
        led_values[0] = - y
    
    # X-Axis (side)
    if x > POS_THRESHOLD:
        led_values[2] = x
    elif x < -POS_THRESHOLD:
        led_values[6] = - x

    # Set LEDs
    for i in range(8):
        leds_circle[i].intensity(round(10 * led_values[i]))

def set_all_leds_rgb(rgb: list):
    global leds_rgb

    for led in leds_rgb:
        led.set_intensity(*rgb)


def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_decoded = msg.decode()
    # print(f"New message on topic '{topic_str}': {msg_decoded}")
    
    if topic_str == CAMERA_DETECT_TOPIC:
        
        # If face not found, stop motors
        if msg_decoded == FACE_NOT_FOUND:
            set_motors_speed(0, 0)
            return

        pos = json.loads(msg_decoded)
        x = pos.get("x") - CAMERA_WIDTH//2
        y = pos.get("y") - CAMERA_HEIGHT//2

        set_motors_speed(x, y)
        # set_leds_circle(x, y)

def connect_to_mqtt():
    global client

    client = MQTTClient(THYMIO_CLIENT_ID, MQTT_BROKER, MQTT_PORT)

    if mqtt_callback is not None:
        client.set_callback(mqtt_callback)

    client.connect()
    print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}')
    client.subscribe(CAMERA_DETECT_TOPIC)
    print(f'Subscribed to topic {CAMERA_DETECT_TOPIC}')


def handle_buttons():
    global buttons, motors, thymio_status

    # If center button pressed for 5s, restart the Thymio
    timer = 0
    while buttons.get_status()[2]:
        motors.set_speed(0, 0)

        time.sleep(0.1)
        timer += 0.1

        if timer > 5:
            print("Resetting Thymio3 ...")
            kill_all()

    # If both side buttons pressed for 1s, stop/start the Thymio
    counter = 0
    while buttons.get_status()[1] and buttons.get_status()[4]:
        motors.set_speed(0, 0)

        time.sleep(0.1)
        counter += 1

        if counter == 10:
            if thymio_status == "Stopped":
                thymio_status = "Running"
                set_all_leds_rgb([0, 16, 0])
                print("Thymio running !")

            elif thymio_status == "Running":
                thymio_status = "Stopped"
                set_all_leds_rgb([16, 0, 0])
                print("Thymio stopped !")


def kill_all():
    global client
    thymio.turn_off_all()
    client.disconnect()
    machine.reset()


def main():
    global client, motors

    connect_to_mqtt()
    set_all_leds_rgb([0, 16, 0])
    print('\nThymio is ready!\n')

    try:
        while True:
            handle_buttons()
            client.check_msg()
            time.sleep(0.01)

    finally:
        kill_all()


if __name__ == "__main__":
    main()
