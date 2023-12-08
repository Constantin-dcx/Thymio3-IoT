import M5
import time
from machine import Pin, PWM
from M5 import Widgets, BtnA, BtnC

# Servo commands parameters
SERVO_PIN = 32
FREQ = 50
MIN_DUTY = 33
MAX_DUTY = 88
PULSE_DELAY = 0.025
STEP = 1

label_close = None
label_open = None
servo = None

last_pulse = MIN_DUTY


BG_COLOR = 0x000000  # BLACK
WHITE = 0xffffff
GREY = 0x666666

def setup():
  global label_close, label_open, servo

  servo = PWM(Pin(SERVO_PIN), FREQ)
  M5.begin()
  Widgets.fillScreen(BG_COLOR)
  label_close = Widgets.Label("Close", 20, 200, 1.0, WHITE, BG_COLOR, Widgets.FONTS.DejaVu24)
  label_open = Widgets.Label("Open", 225, 200, 1.0, WHITE, BG_COLOR, Widgets.FONTS.DejaVu24)


def set_pulse(pulse: int):
  global last_pulse
#   print(f"Set pulse to {pulse}")
  servo.duty(pulse)
  last_pulse = pulse

def go_to_pulse(target_pulse: int, delay: int = PULSE_DELAY, step: int = STEP):
  global last_pulse
  start_pulse = last_pulse
  sign = (target_pulse > start_pulse) * 2 - 1
  for pulse in range(start_pulse, target_pulse + sign, step * sign):
    set_pulse(pulse)
    time.sleep(delay)

def open(delay: int = PULSE_DELAY, step: int = STEP):
  print("Opening...")
  go_to_pulse(MIN_DUTY, delay=delay, step=step)
  print("Opened!")

def close(delay: int = PULSE_DELAY, step: int = STEP):
  print("Closing...")
  go_to_pulse(MAX_DUTY, delay=delay, step=step)
  print("Closed!")

def handle_close_pressed():
  global label_close
  label_close.setColor(GREY, BG_COLOR)
  while not BtnA.isReleased():
    M5.update()
  
  label_close.setColor(WHITE, BG_COLOR)
  close()

def handle_open_pressed():
  global label_open
  label_open.setColor(GREY, BG_COLOR)
  while not BtnC.isReleased():
    M5.update()
  
  label_open.setColor(WHITE, BG_COLOR)
  open()

def loop():
  global label_close
  M5.update()

  if BtnA.isPressed():
    print("Close is pressed")
    handle_close_pressed()

  if BtnC.isPressed():
    print("Open is pressed")
    handle_open_pressed()

#   if BtnA.isReleased():  # easy
#     print("isReleased")
#   if BtnA.wasClicked():
#     print("wasClicked")

#   if BtnA.wasPressed():
#     print("wasPressed")
#   if BtnA.wasReleased():
#     print("wasReleased")

#   if M5.BtnA.wasClicked():
#     close()

#   if M5.BtnC.wasClicked():
#     open()




if __name__ == "__main__":
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    from utility import print_error_msg
    print_error_msg(e)
        