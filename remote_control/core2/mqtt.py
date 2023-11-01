import time
from umqtt.simple import MQTTClient

# MQTT Credentials
MQTT_CLIENT_ID = 'core2_client'
MQTT_BROKER = '192.168.1.102'
MQTT_PORT = 1883
MQTT_TOPIC = 'test/topic'

# Publishing interval
PUBLISH_INTERVAL = 1.0  # in seconds, 0.5 means 2 times per second

def mqtt_callback(topic, msg):
    print("New message on topic '{}': {}".format(topic.decode(), msg.decode()))

def connect_to_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}')
    client.subscribe(MQTT_TOPIC)
    print(f'Subscribed to topic {MQTT_TOPIC}')
    
    message_count = 0

    try:
        while True:
            # Publish message
            message = "Message {}".format(message_count)
            client.publish(MQTT_TOPIC, message)
            print("Message sent:", message)
            message_count += 1

            # Wait for the specified interval
            time.sleep(PUBLISH_INTERVAL)

    finally:
        client.disconnect()