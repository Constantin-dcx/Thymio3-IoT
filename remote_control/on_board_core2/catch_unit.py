import time
from machine import Pin, PWM


class CatchUnit:
  SERVO_PIN = 32
  FREQ = 50

  def __init__(self, min_pulse: int = 33, max_pulse: int = 88, 
               pulse_delay: float = 0.025, step: int = 1) -> None:
    
    self._min_pulse = min_pulse
    self._max_pulse = max_pulse
    self._pulse_delay = pulse_delay
    self._step = step
    self.last_pulse = self._min_pulse

    self._servo = PWM(Pin(self.SERVO_PIN), self.FREQ)
    print("CatchUnit initiated.")
    print("\nWARNING: Please make sur the gripper is fully opened.")

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

  def _set_pulse(self, pulse: int):
    self._servo.duty(pulse)
    self.last_pulse = pulse
