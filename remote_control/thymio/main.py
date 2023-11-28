from thymio import LEDS_CIRCLE
import thymio
import json
import time
from umqtt.simple import MQTTClient
from config import *

ACC_THRESHOLD = 0.2
MAX_SPEED = 750

thymio.disable_behaviors()
leds = [LEDS_CIRCLE(i) for i in range(8)]
motors = thymio.MOTORS()


def handle_acceleration(acc_x: float, acc_y: float):
    led_values = [0 for _ in range(8)]
    front_speed, turn_speed = 0, 0

    # Y-Axis (front)
    if acc_y > ACC_THRESHOLD:
        led_values[4] = acc_y
    elif acc_y < -ACC_THRESHOLD:
        led_values[0] = - acc_y
    
    if abs(acc_y) > ACC_THRESHOLD:
        front_speed = - acc_y * MAX_SPEED

    # X-Axis (side)
    if acc_x > ACC_THRESHOLD:
        led_values[2] = acc_x
    elif acc_x < -ACC_THRESHOLD:
        led_values[6] = - acc_x

    if abs(acc_x) > ACC_THRESHOLD:
        turn_speed = acc_x * MAX_SPEED / 2
        # Invert turn speed if going backwards
        if front_speed < 0:
            turn_speed = - turn_speed

    # Set LEDs
    for i in range(8):
        leds[i].intensity(round(10 * led_values[i]))

    # Set Motors
    left_speed = int(front_speed + turn_speed)
    right_speed = int(front_speed - turn_speed)
    # print(f'Setting motors speed: {left_speed=}, {right_speed=}')
    motors.set_speed(left_speed, right_speed)


def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_decoded = msg.decode()
    # print(f"New message on topic '{topic_str}': {msg_decoded}")
    
    if topic_str == IMU_TOPIC:
        acc = json.loads(msg_decoded)

        handle_acceleration(acc.get("x"), acc.get("y"))

def connect_to_mqtt():
    global client

    client = MQTTClient(THYMIO_CLIENT_ID, MQTT_BROKER, MQTT_PORT)

    if mqtt_callback is not None:
        client.set_callback(mqtt_callback)

    client.connect()
    print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}')
    client.subscribe(IMU_TOPIC)
    print(f'Subscribed to topic {IMU_TOPIC}')


def main():
    global client

    connect_to_mqtt()

    try:
        while True:
            # Receive messages
            client.check_msg()

            # Wait for the specified interval
            time.sleep(0.01)

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
