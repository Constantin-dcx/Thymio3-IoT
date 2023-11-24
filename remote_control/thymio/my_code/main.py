from thymio import LEDS_CIRCLE
import thymio
import json
import time
from umqtt.simple import MQTTClient

# MQTT Credentials
MQTT_CLIENT_ID = 'thymio_client'
MQTT_BROKER = '192.168.1.101'
MQTT_PORT = 1883
MQTT_TOPIC = 'test/topic'
IMU_TOPIC = "core2/IMU"

thymio.disable_behaviors()
leds = [LEDS_CIRCLE(i) for i in range(8)]

ACC_THRESHOLD = 0.1


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

    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}')
    client.subscribe(MQTT_TOPIC)
    print(f'Subscribed to topic {MQTT_TOPIC}')
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
