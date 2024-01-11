import json
import thymio
import time
from config import *
from umqtt.simple import MQTTClient


ACC_THRESHOLD = 0.15
MAX_ACC = 1.0
MAX_SPEED = 750

leds = [thymio.LEDS_CIRCLE(i) for i in range(8)]
motors = thymio.MOTORS()


def sign(x):
    return (x > 0) - (x < 0)

def map_acc_to_speed(acc: float, max_speed: int):
    if abs(acc) < ACC_THRESHOLD:
        return 0
    
    return sign(acc) * (abs(acc) - ACC_THRESHOLD) / (MAX_ACC - ACC_THRESHOLD) * max_speed
    
def set_motors_speed(acc_x: float, acc_y: float):

    # Y-Axis (front)
    front_speed = map_acc_to_speed(-acc_y, max_speed=MAX_SPEED)

    # X-Axis (side)
    turn_speed = map_acc_to_speed(acc_x, max_speed=MAX_SPEED//4)
    # Invert turn speed if going backwards
    if front_speed < 0:
        turn_speed = - turn_speed

    # Set Motors
    left_speed = int(front_speed + turn_speed)
    right_speed = int(front_speed - turn_speed)
    motors.set_speed(left_speed, right_speed)

def set_leds(acc_x: float, acc_y: float):
    led_values = [0 for _ in range(8)]
    
    # Y-Axis (front)
    if acc_y > ACC_THRESHOLD:
        led_values[4] = acc_y
    elif acc_y < -ACC_THRESHOLD:
        led_values[0] = - acc_y
    
    # X-Axis (side)
    if acc_x > ACC_THRESHOLD:
        led_values[2] = acc_x
    elif acc_x < -ACC_THRESHOLD:
        led_values[6] = - acc_x

    for i in [1, 3, 5, 7]:
        led_prev = led_values[(i-1)%8]
        led_next = led_values[(i+1)%8]
        if led_prev and led_next:
            led_values[i] = (led_prev + led_next) / 2

    # Set LEDs
    for i in range(8):
        leds[i].intensity(round(16 * led_values[i]))

def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_decoded = msg.decode()
    
    if topic_str == IMU_TOPIC:
        acc = json.loads(msg_decoded)
        acc_x, acc_y = acc.get("x"), acc.get("y")

        set_motors_speed(acc_x, acc_y)
        set_leds(acc_x, acc_y)

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

    print('\nThymio is ready!\n')

    try:
        while True:
            # Receive messages
            client.check_msg()

            # Wait for the specified interval
            time.sleep(0.01)

    finally:
        client.disconnect()
        thymio.turn_off_all()


if __name__ == "__main__":
    main()
