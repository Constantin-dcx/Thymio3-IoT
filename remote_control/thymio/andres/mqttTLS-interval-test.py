import network
import time
from umqtt.simple import MQTTClient

# WiFi Credentials, in order of priority
wifi_credentials = [
    {"ssid": "my ssid 1", "password": "my password 1"},
    {"ssid": "my ssid 2", "password": "my password 2"},
]

# MQTT Credentials
MQTT_CLIENT_ID = 'ESP32_client'
MQTT_BROKER = 'mqtt.thymio.eu'
MQTT_PORT = 8883  # Changed to 8883, which is the standard port for MQTT over TLS
MQTT_TOPIC = 'test/topic'

# Intermediate certificate
CERT_PATH = '/intermediate_cert.pem'

# Publishing interval
PUBLISH_INTERVAL = 0.5  # in seconds, 0.5 means 2 times per second

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    available_ssids = {ssid.decode('utf-8'): bssid for ssid, bssid, *_ in networks}
    
    for ssid_info in wifi_credentials:
        ssid = ssid_info["ssid"]
        if ssid in available_ssids:
            print(f'Connecting to WiFi network "{ssid}"...')
            wlan.connect(ssid, ssid_info["password"])
            while wlan.ifconfig()[0] == '0.0.0.0':
                pass
            print(f'Successfully connected to WiFi network "{ssid}".')
            return True
        else:
            print(f'WiFi network "{ssid}" is not available.')
    
    return False

def mqtt_callback(topic, msg):
    print("New message on topic '{}': {}".format(topic.decode(), msg.decode()))

def connect_to_mqtt():
    with open(CERT_PATH, 'r') as f:
        cert_content = f.read()
    
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT, ssl=True, ssl_params={'cert': cert_content})
    client.set_callback(mqtt_callback)
    client.connect()
    print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT} with TLS')
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
            
            # Receive messages
            client.check_msg()

            # Wait for the specified interval
            time.sleep(PUBLISH_INTERVAL)

    finally:
        client.disconnect()

if connect_to_wifi():
    connect_to_mqtt()
else:
    print("Failed to connect to WiFi network.")