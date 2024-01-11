from machine import Pin, PWM


class CatchUnit:
  FREQ = 50

  def __init__(self, pin: int, min_pulse: int = 34, max_pulse: int = 90) -> None:
    self._pin = pin
    self._min_pulse = min_pulse
    self._max_pulse = max_pulse
    self._servo = PWM(Pin(self._pin), self.FREQ)

    print("CatchUnit initiated.")

  def open(self):
    print("Opening...")
    self.set_pulse(self._min_pulse)
    print("Opened!")

  def close(self):
    print("Closing...")
    self.set_pulse(self._max_pulse)
    print("Closed!")

  def set_pulse(self, pulse: int):
    self._servo.duty(pulse)
