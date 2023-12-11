import M5
import time
from catch_unit import CatchUnit
from config import *
from M5 import Widgets
from umqtt.simple import MQTTClient


REFRESH_TIME = 0.01

# Colors
BLACK = 0x000000
WHITE = 0xffffff
GREY = 0x666666

TEXT_HEIGHT = 97

# UI globals
label_status = None

client = None
gripper = None


def setup():
  global label_status, gripper

  M5.begin()
  Widgets.fillScreen(BLACK)

  label_status = Widgets.Label("Connecting...", 28, TEXT_HEIGHT, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu40)
  connect_to_mqtt()
  wifi_image = Widgets.Image("img/wifi.png", 300, 0)
  label_status.setText("Connected!")
  label_status.setCursor(x=45, y=TEXT_HEIGHT)

  gripper = CatchUnit()


def open_gripper():
  global gripper, label_status, client
  label_status.setText("Opening...")
  label_status.setCursor(x=57, y=TEXT_HEIGHT)
  gripper.open()

  client.publish(GRIPPER_STATUS, GRIPPER_FINISHED)
  label_status.setText("Open!")
  label_status.setCursor(x=98, y=TEXT_HEIGHT)

def close_gripper():
  global gripper, label_status, client
  label_status.setText("Closing...")
  label_status.setCursor(x=68, y=TEXT_HEIGHT)
  gripper.close()

  client.publish(GRIPPER_STATUS, GRIPPER_FINISHED)
  label_status.setText("Closed!")
  label_status.setCursor(x=85, y=TEXT_HEIGHT)


def mqtt_callback(topic, msg):

    topic_str = topic.decode()
    # print(f"New message on topic '{topic_str}': {msg}")
    
    if topic_str == GRIPPER_ACTION:
      if msg == GRIPPER_CLOSE:
        close_gripper()
      elif msg == GRIPPER_OPEN:
        open_gripper()


def connect_to_mqtt():
    global client
    
    client = MQTTClient(ON_BOARD_CORE2_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    print(f'Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...')

    client.set_callback(mqtt_callback)
    client.connect()
    print('Successfully connected to MQTT broker !')

    client.subscribe(GRIPPER_ACTION)
    print(f'Subscribed to topic {GRIPPER_ACTION}')


def loop():
  global client, gripper

  M5.update()
  client.check_msg()
  
  time.sleep(REFRESH_TIME)



if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    from utility import print_error_msg
    print_error_msg(e)
  finally:
    client.disconnect()
