import json
import machine


class UnitV2:
    PROTOCOL_START = b'{'[0]
    GET_IP_TIMEOUT_MS = 5_000

    def __init__(self, tx: int = 32, rx: int = 33) -> None:
        # Start serial communication
        self.uart = machine.UART(1, tx=tx, rx=rx)
        self.uart.init(115200, bits=8, parity=None, stop=1)

    def get_ip(self):
        self.uart.write("{\"get_ip\": \"\"}\r\n")

    def read_serial(self): 
        if not self.uart.any():
            return

        data = self.uart.readline()
        if data is None or data[0] != self.PROTOCOL_START:
            return

        # Decode json data
        try:
            data_decoded = json.loads(data)
            return data_decoded
        except ValueError:
            print(f'WARNING: Could not decode json data from UnitV2: \n{data}')
            return
        