import M5
import time
from machine import Pin, PWM
from M5 import Widgets


SERVO_PIN = 32
FREQ = 50
MIN_ANGLE, MAX_ANGLE = 0, 180
RESOLUTION = 1024

# MIN_PULSE_MS, MAX_PULSE_MS = 1, 2
# MIN_DUTY = int(MIN_PULSE_MS / 1000 * FREQ * RESOLUTION)
# MAX_DUTY = int(MAX_PULSE_MS / 1000 * FREQ * RESOLUTION)
MIN_DUTY = 25
MAX_DUTY = 88

PULSE_DELAY = 0.025
STEP = 1

label = None
servo = None

last_pulse = MIN_DUTY


def setup():
  global label, servo

  servo = PWM(Pin(SERVO_PIN), FREQ)
  M5.begin()
  Widgets.fillScreen(0x222222)
  label = Widgets.Label("ON", 104, 79, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu72)

def set_pulse(pulse: int):
  global last_pulse
  print(f"Set pulse to {pulse}")
  servo.duty(pulse)
  last_pulse = pulse


# def compute_pulse(angle: int):
#   global label, servo
#   pulse = int((angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE) * (MAX_DUTY - MIN_DUTY) + MIN_DUTY)
#   return pulse
# 
# def go_to_angle(angle: int, delay: int = PULSE_DELAY, step: int = STEP):
#   target_pulse = compute_pulse(angle)
#   go_to_pulse(target_pulse, delay=delay, step=step)

def go_to_pulse(target_pulse: int, delay: int = PULSE_DELAY, step: int = STEP):
  global last_pulse
  start_pulse = last_pulse
  sign = (target_pulse > start_pulse) * 2 - 1
  for pulse in range(start_pulse, target_pulse + sign, step * sign):
    set_pulse(pulse)
    time.sleep(delay)

def open(delay: int = PULSE_DELAY, step: int = STEP):
  go_to_pulse(MIN_DUTY, delay=delay, step=step)

def close(delay: int = PULSE_DELAY, step: int = STEP):
  go_to_pulse(MAX_DUTY, delay=delay, step=step)


def loop():
  global label
  M5.update()




if __name__ == "__main__":
  try:
    setup()
    # while True:
    #   loop()
  except (Exception, KeyboardInterrupt) as e:
    from utility import print_error_msg
    print_error_msg(e)
        