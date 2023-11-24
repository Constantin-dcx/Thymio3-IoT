import M5
from M5 import Widgets, Imu
import time
import json
from umqtt.simple import MQTTClient

label3 = None
line0 = None
label4 = None
line1 = None
label5 = None


acc_x = None
acc_y = None
acc_z = None


# MQTT Credentials
MQTT_CLIENT_ID = 'core2_client'
MQTT_BROKER = '192.168.1.101'
MQTT_PORT = 1883
IMU_TOPIC = 'core2/IMU'

client = None
last_time = 0

PUBLISH_INTERVAL_MS = 150


def setup():
  global label3, line0, label4, line1, label5, acc_x, acc_y, acc_z, client

  M5.begin()
  Widgets.fillScreen(0x222222)
  label3 = Widgets.Label("label", 167, 14, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  line0 = Widgets.Line(73, 100, 123, 100, 0xffffff)
  label4 = Widgets.Label("label", 166, 54, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  line1 = Widgets.Line(124, 144, 174, 144, 0xffffff)
  label5 = Widgets.Label("label", 166, 95, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # Connect to MQTT
  client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
  client.connect()
  print(f'Successfully connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}')

def loop():
  global label3, line0, label4, line1, label5, acc_x, acc_y, acc_z, last_time, client
  M5.update()
  acc_x = -(Imu.getAccel())[0]
  acc_y = (Imu.getAccel())[1]
  acc_z = (Imu.getAccel())[2]
  label3.setText(str((str('x:') + str(("%.1f"%(acc_x))))))
  label4.setText(str((str('y:') + str(("%.1f"%(acc_y))))))
  label5.setText(str((str('z:') + str(("%.1f"%(acc_z))))))
  line0.setPoints(x0=160, y0=120, x1=(int(160 + 100 * acc_x)), y1=120)
  line1.setPoints(x0=160, y0=120, x1=160, y1=(int(120 + 100 * acc_y)))

  if time.ticks_diff(time.ticks_ms(), last_time) > PUBLISH_INTERVAL_MS:
    # Publish message
    message = {"x": acc_x, "y": acc_y, "z": acc_z}
    msg_json = json.dumps(message)
    client.publish(IMU_TOPIC, msg_json)
    print("Message sent:", message)
    last_time = time.ticks_ms()



if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
