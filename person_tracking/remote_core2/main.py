import M5
import time
import urequests
from config import *
from umqtt.simple import MQTTClient


client = None
unitv2_ip = None


def setup():
    global client

    M5.begin()

    # Connect to MQTT
    client = MQTTClient(TRACKING_REMOTE_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.set_callback(mqtt_callback)
    print(f'Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...')
    client.connect()
    print('Successfully connected to MQTT broker !')
    client.subscribe(CAMERA_IP_POST_TOPIC)

    get_unitv2_ip()


def get_unitv2_ip(retry_interval_ms = 5_000):
    global client

    client.publish(CAMERA_IP_GET_TOPIC, "")

    last_time = time.ticks_ms()
    while unitv2_ip is None:
        client.check_msg()
        time.sleep(0.1)

        # Ask again if IP not received in `retry_interval_ms`
        if time.ticks_diff(time.ticks_ms(), last_time) > retry_interval_ms:
            print(f"WARNING: Could not get UnitV2 ip address in {retry_interval_ms}ms. Retrying ...")
            client.publish(CAMERA_IP_GET_TOPIC, "")
            last_time = time.ticks_ms()


def mqtt_callback(topic, msg):
    global unitv2_ip

    topic_str = topic.decode()
    msg_decoded = msg.decode()
    
    if topic_str == CAMERA_IP_POST_TOPIC:
        unitv2_ip = msg_decoded
        print(f"Received UnitV2 IP address: '{unitv2_ip}'")
        

def parse_multipart_stream(response):
    buffer = bytearray()
    while True:
        chunk = response.raw.read(4096)  # Read chunks from the response
        if not chunk:
            break

        buffer.extend(chunk)
        while True:
            # Find the boundary in the buffer
            boundary_index = buffer.find(b'--frame')
            if boundary_index == -1:
                # Boundary not found - get more data
                break

            # Skip the boundary and headers
            end_of_headers = buffer.find(b'\r\n\r\n', boundary_index)
            if end_of_headers == -1:
                break

            # Extract the frame
            start_of_frame = end_of_headers + 4
            end_of_boundary = buffer.find(b'--frame', start_of_frame)
            if end_of_boundary == -1:
                break

            frame_data = buffer[start_of_frame:end_of_boundary]
            buffer = buffer[end_of_boundary:]

            yield frame_data

def fetch_and_display_stream(url):
    # Connect to the video feed
    response = urequests.get(url, stream=True)

    try:
        for frame_data in parse_multipart_stream(response):
            # Display the image on LCD
            M5.Lcd.drawImage(frame_data)
    
    finally:
        response.close()


if __name__ == '__main__':
    try:
        setup()

        stream_url = f'http://{unitv2_ip}/video_feed'
        print(f"Ready to stream from {stream_url} !")

        fetch_and_display_stream(url=stream_url)

    except (Exception, KeyboardInterrupt) as e:
        from utility import print_error_msg
        print_error_msg(e)

  
