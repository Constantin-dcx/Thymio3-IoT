import thymio
import wifi

thymio.disable_behaviors()

voltage = thymio.get_battery_voltage()
print(f"\nBattery voltage: {voltage} mV.\n")

wifi.connect()