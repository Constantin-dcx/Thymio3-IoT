import json
import time
from machine import Pin, PWM


class CatchUnit:
  SERVO_PIN = 32
  FREQ = 50
  LAST_PULSE_FILE = "servo_position.json"

  def __init__(self, min_pulse: int = 26, max_pulse: int = 90, 
               pulse_delay: float = 0.025, step: int = 1, 
               save_file: bool = False) -> None:
    
    self._min_pulse = min_pulse
    self._max_pulse = max_pulse
    self._pulse_delay = pulse_delay
    self._step = step
    self._save_file = save_file
    self._load_last_pulse()
    self._servo = PWM(Pin(self.SERVO_PIN), self.FREQ)

    print("CatchUnit initiated.")

  def open(self, delay: int = None, step: int = None):
    print("Opening...")
    self.go_to_pulse(self._min_pulse, delay=delay, step=step)
    print("Opened!")

  def close(self, delay: int = None, step: int = None):
    print("Closing...")
    self.go_to_pulse(self._max_pulse, delay=delay, step=step)
    print("Closed!")

  def go_to_pulse(self, target_pulse: int, delay: int = None, step: int = None):
    start_pulse = self.last_pulse

    delay = delay if delay else self._pulse_delay
    step = step if step else self._step

    sign = (target_pulse > start_pulse) * 2 - 1
    for pulse in range(start_pulse, target_pulse + sign, step * sign):
      self._set_pulse(pulse)
      time.sleep(delay)

    self._save_last_pulse()

  def _set_pulse(self, pulse: int):
    self._servo.duty(pulse)
    self.last_pulse = pulse

  def _save_last_pulse(self):
    if self._save_file:
      data = {"pulse": self.last_pulse}
      with open(self.LAST_PULSE_FILE, "w") as f:
        json.dump(data, f)

  def _load_last_pulse(self):
    if self._save_file:
      try:
        with open(self.LAST_PULSE_FILE, "r") as f:
          data = json.load(f)
          self.last_pulse = data["pulse"]
          print(f"Found last pulse: {self.last_pulse}")
      except (OSError, ValueError) as error:
        print(f"\nERROR: Could not find last pulse in {self.LAST_PULSE_FILE}: {error}")
        print("ERROR: Please make sur the gripper is fully opened.\n")
        self.last_pulse = self._min_pulse

    else:
      print("\nWARNING: Please make sure the gripper is fully opened.\n")
      self.last_pulse = self._min_pulse
