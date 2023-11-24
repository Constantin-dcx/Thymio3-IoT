from thymio import LEDS_CIRCLE
import thymio
import json
import time
from umqtt.simple import MQTTClient
from config import *

ACC_THRESHOLD = 0.1

thymio.disable_behaviors()
leds = [LEDS_CIRCLE(i) for i in range(8)]

def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_decoded = msg.decode()
    print(f"New message on topic '{topic_str}': {msg_decoded}")
    
    if topic_str == IMU_TOPIC:
        acc = json.loads(msg_decoded)
        acc_x = acc.get("x")
        acc_y = acc.get("y")

        led_values = [0 for _ in range(8)]
        if acc_x > ACC_THRESHOLD:
            led_values[2] = acc_x
        elif acc_x < -ACC_THRESHOLD:
            led_values[6] = - acc_x

        if acc_y > ACC_THRESHOLD:
            led_values[4] = acc_y
        elif acc_y < -ACC_THRESHOLD:
            led_values[0] = - acc_y

        for i in range(8):
            leds[i].intensity(round(10 * led_values[i]))


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
