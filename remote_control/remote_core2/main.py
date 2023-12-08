import json
import math
import M5
import time
from config import *
from M5 import Widgets, Imu, BtnA, BtnC
from umqtt.simple import MQTTClient

# Colors
BLACK = 0x000000
WHITE = 0xffffff
GREY = 0x666666

# UI globals
label_x = None
line_x = None
label_y = None
line_y = None
label_z = None

label_close = None
label_open = None

# Sensors globals
acc_x = None
acc_y = None
acc_z = None

PUBLISH_INTERVAL_MS = 150

client = None

is_close_pressed = False
is_open_pressed = False
last_time = 0
is_gripper_finished = True


def setup():
  global label_x, line_x, label_y, line_y, label_z, client, label_close, label_open

  M5.begin()
  Widgets.fillScreen(BLACK)

  # Connect to MQTT
  client = MQTTClient(REMOTE_CORE2_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
  print(f'Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...')
  client.set_callback(mqtt_callback)
  client.connect()
  wifi_image = Widgets.Image("img/wifi.png", 300, 0)
  print('Successfully connected to MQTT broker !')
  client.subscribe(GRIPPER_STATUS)

  # IMU UI
  label_x = Widgets.Label("x:", 166, 14, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu18)
  line_x = Widgets.Line(160, 120, 160, 120, WHITE)
  label_y = Widgets.Label("y:", 166, 54, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu18)
  line_y = Widgets.Line(160, 120, 160, 120, WHITE)
  label_z = Widgets.Label("z:", 166, 95, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu18)

  # Open/Close buttons
  label_close = Widgets.Label("Close", 20, 200, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu24)
  label_open = Widgets.Label("Open", 225, 200, 1.0, WHITE, BLACK, Widgets.FONTS.DejaVu24)


def loop():
  global label_x, line_x, label_y, line_y, label_z, acc_x, acc_y, acc_z, last_time
  M5.update()

  # Get IMU data
  acc_x = -(Imu.getAccel())[0]
  acc_y = (Imu.getAccel())[1]
  acc_z = (Imu.getAccel())[2]

  # Update IMU UI
  label_x.setText(f'x: {round(acc_x*10)/10}')
  label_y.setText(f'y: {round(acc_y*10)/10}')
  label_z.setText(f'z: {round(acc_z*10)/10}')
  line_x.setPoints(x0=160, y0=120, x1=(int(160 + 100 * acc_x)), y1=120)
  line_y.setPoints(x0=160, y0=120, x1=160, y1=(int(120 + 100 * acc_y)))

  # Publish IMU data
  if time.ticks_diff(time.ticks_ms(), last_time) > PUBLISH_INTERVAL_MS:
    message = {"x": acc_x, "y": acc_y, "z": acc_z}
    msg_json = json.dumps(message)
    client.publish(IMU_TOPIC, msg_json)
    # print("Message sent:", message)
    last_time = time.ticks_ms()

  handle_buttons()

def mqtt_callback(topic, msg):
  global is_gripper_finished
  if topic.decode() == GRIPPER_STATUS:
    if msg == GRIPPER_FINISHED:
      # print("Gripper Finished!")
      is_gripper_finished = True

def wait_for_gripper_finished( timeout_ms: int = 5_000):
  start_time = time.ticks_ms()

  while not is_gripper_finished:
    if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
      print(f"ERROR: Gripper command timed out in {timeout_ms} ms. Command aborted.")
      print("ERROR: Please make sure the on-board Core2 is online.")

      break
    
    client.check_msg()
    time.sleep(0.05)

def handle_buttons(blocking: bool = True):
  global label_close, label_open, is_close_pressed, is_open_pressed, client, is_gripper_finished

  # Gripper Close
  if not is_close_pressed and BtnA.isPressed():
    label_close.setColor(GREY, BLACK)
    is_close_pressed = True

  if is_close_pressed and BtnA.isReleased():
    label_close.setColor(WHITE, BLACK)
    is_close_pressed = False
    is_gripper_finished = False
    client.publish(GRIPPER_ACTION, GRIPPER_CLOSE)

    if blocking:
      wait_for_gripper_finished()

  # Gripper Open
  if not is_open_pressed and BtnC.isPressed():
    label_open.setColor(GREY, BLACK)
    is_open_pressed = True

  if is_open_pressed and BtnC.isReleased():
    label_open.setColor(WHITE, BLACK)
    is_open_pressed = False
    is_gripper_finished = False
    client.publish(GRIPPER_ACTION, GRIPPER_OPEN)

    if blocking:
      wait_for_gripper_finished()


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    from utility import print_error_msg
    print_error_msg(e)
