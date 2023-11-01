# -*- coding: utf-8 -*-
"""
This code is meant to run on a microcontroller, such as the ESP32, and works with a Thymio robot using Bluetooth Low Energy (BLE). 
The system handles connections and disconnections from a BLE client, receives Python code sent over BLE, 
saves it to a file, and executes it. It can also stop the code execution on demand.
"""

from micropython import const
import struct
import bluetooth
import machine 
import _thread
import time
import re
import thymio
import os

def update():
    if "update.py" in os.listdir():
        try:
            with open("update.py", "r") as file:
                code = file.read()
                exec(code)
                print("Archivo 'update.py' importado exitosamente.")
        except Exception as e:
            print("Error al importar 'update.py':", e)
            try:
                os.remove("update.py")
                print(f"El archivo update.py se ha eliminado correctamente.")
            except OSError as e:
                print(f"Error al eliminar el archivo update.py: {e}")
    else:
        print("No hay actualizaciones programadas")

update()
        
# Global variables
accumulator = "" # Variable to accumulate the received data
state = 'IDLE' # State of bluetooth manager
active = [False] # Variable to stop the execution of the code

#--------------------------------------------------------------------------------------------
# advertising_payload: Function to create the advertising payload
#--------------------------------------------------------------------------------------------
def advertising_payload(name=None, services=None):
    _ADV_TYPE_FLAGS = const(0x01)
    _ADV_TYPE_NAME = const(0x09)
    _ADV_TYPE_UUID16_COMPLETE = const(0x3)
    _ADV_TYPE_UUID32_COMPLETE = const(0x5)
    _ADV_TYPE_UUID128_COMPLETE = const(0x7)

    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(_ADV_TYPE_FLAGS, struct.pack("B", 0x06))

    if name:
        _append(_ADV_TYPE_NAME, name)
    else :
        _append(_ADV_TYPE_NAME, 'Thymio 3-2')

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    return payload


#--------------------------------------------------------------------------------------------
# WebsocketManager
#--------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------
# BluetoothManager
#--------------------------------------------------------------------------------------------
class BluetoothManager:
    def __init__(self, name="Thymio 3-2"):
        self._IRQ_CENTRAL_CONNECT = const(1)
        self._IRQ_CENTRAL_DISCONNECT = const(2)
        self._IRQ_GATTS_WRITE = const(3)
        self._IRQ_GATTS_READ_REQUEST = const(4)
        
        self.UART_SERVICE_UUID = bluetooth.UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
        self.UART_RX_CHAR_UUID = bluetooth.UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")
        self.UART_TX_CHAR_UUID = bluetooth.UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
        
        self._UART_RX = (self.UART_RX_CHAR_UUID, bluetooth.FLAG_WRITE)
        self._UART_TX = (self.UART_TX_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
        self.UART_SERVICE = (self.UART_SERVICE_UUID, (self._UART_RX, self._UART_TX,),)
        self.SERVICES = (self.UART_SERVICE,)

        self.ble = bluetooth.BLE()
        
        self.ble.active(True)
        self.ble.irq(self.bt_irq)
        ((self.h_rx, self.h_tx,),) = self.ble.gatts_register_services(self.SERVICES)
        
        self.conn_handle = None
        self.addr_type = None
        self.addr = None

        self.name = name

        self.on_connect = None
        self.on_disconnect = None
        self.on_message_received = None
        
        self.connected = False
        
        self.start_advertising()

    def start_advertising(self):
        print("Starting advertising "+self.name+"...")
        payload = advertising_payload(self.name)
        self.ble.gap_advertise(interval_us=500000, adv_data=payload)

    def set_on_connect(self, callback):
        self.on_connect = callback

    def set_on_disconnect(self, callback):
        self.on_disconnect = callback
        
    def set_on_message_received(self, callback):
        self.on_message_received = callback
        
    def send_message(self, message):
        bytes_message = message.encode('utf-8')
        self.ble.gatts_notify(self.conn_handle, self.h_tx, bytes_message)

    def bt_irq(self, event, data):
        # Handles BLE interrupts
        if event == self._IRQ_CENTRAL_CONNECT and not self.connected:
            # A central device has connected
            self.connected = True
            self.conn_handle, self.addr_type, self.addr = data
            if self.on_connect:
                self.on_connect(data)
        elif event == self._IRQ_CENTRAL_DISCONNECT and self.connected:
            # A central device has disconnected
            self.connected = False
            self.conn_handle = None
            self.addr_type = None
            self.addr = None
            self.start_advertising()
            if self.on_disconnect:
                self.on_disconnect(data)
        elif event == self._IRQ_GATTS_WRITE or event == self._IRQ_GATTS_READ_REQUEST:
             # This device's characteristic was written to from a remote device
            self.conn_handle, value_handle = data
            value = self.ble.gatts_read(value_handle)
            decodedMessage = value.decode('utf-8')
            if self.on_message_received:
                self.on_message_received(decodedMessage)
                
bluetoothManager = BluetoothManager('Thymio 3-2')

#--------------------------------------------------------------------------------------------
# on_connect: Function to be executed when a BLE client connects
#--------------------------------------------------------------------------------------------
def on_connect(data):
    global accumulator, state
    print('BLE client connected')
    accumulator = ''
    state = 'IDLE'
    active[0] = False
    
bluetoothManager.set_on_connect(on_connect)

#--------------------------------------------------------------------------------------------
# on_disconnect: Function to be executed when a BLE client disconnects
#--------------------------------------------------------------------------------------------
def on_disconnect(data):
    global accumulator, state
    print('BLE client disconnected')
    accumulator = ''
    state = 'IDLE'
    active[0] = False
    machine.reset()

bluetoothManager.set_on_disconnect(on_disconnect)
        
#--------------------------------------------------------------------------------------------

def calculate_indentation(line):
    indentation = 0
    for char in line:
        if char == " ":
            indentation += 1
        elif char == "\t":
            indentation += 4
        else:
            break
    return " " * indentation
        
#--------------------------------------------------------------------------------------------

def detect_indentation_type(code):
    lines = code.split('\n')

    for line in lines:
        if line.strip() and not line.startswith("#"):
            if "\t" in line:
                return "tab"
            elif line.startswith("    "):
                return "4 spaces"
            elif line.startswith("  "):
                return "2 spaces"
            
    return None
        
def convert_indentations(code):
    identation_type = detect_indentation_type(code)
    
    if identation_type == "tab":
        return re.sub(r'\t', '    ', code)
    if identation_type == "2 spaces":
        return re.sub(r'  ', '    ', code)
    if identation_type == "4 spaces":
        return code
    if identation_type == None:
        return code

#--------------------------------------------------------------------------------------------
# add_breaks: Function to add the break statement after each instruction in the code
#--------------------------------------------------------------------------------------------
def add_breaks(codeNotNormalized):
    code = convert_indentations(codeNotNormalized)
    modified_code = """
    \nclass StopThread(Exception):
    def __init__(self, message='Thread stopped'):
        self.message = message
        super().__init__(self.message)
    """
    lines = code.split('\n')
    previous_indent = ""

    for line in lines:
        stripped_line = line.strip()

        # Ignorar líneas vacías y comentarios
        if not stripped_line or stripped_line.startswith("#") or "import " in stripped_line or "return " in stripped_line or "break" in stripped_line:
            modified_code += line + "\n"
            continue

        # Agregar la sentencia if not active[0]: raise StopThread() después de cada instrucción
        previous_indent = calculate_indentation(line)
        
        if not stripped_line.endswith(":"):
            modified_code += line + "\n"
        elif stripped_line.endswith(":"):
            modified_code += line + "\n"
            modified_code += previous_indent + "    if not active[0]: raise StopThread()\n"
        else:
            modified_code += previous_indent + line + "\n"
    return modified_code
        
#--------------------------------------------------------------------------------------------
# running: Function to execute python code from script1.py in a new thread
#--------------------------------------------------------------------------------------------
def sendMessageInterne(message):
    bluetoothManager.send_message(message)
    print(f'sendMessage {message}')

def running():
    global active, bluetoothManager, sendMessageInterne
    try:
        def run_code():
            global active, state, accumulator 

            #new_thread = threading.Thread(target=run_code, args=())
            try:
                code = open("script1.py").read()
                codeWithBreaks = add_breaks(code)
                print("start running code from file script1.py:\n", codeWithBreaks)
                exec(codeWithBreaks, {"active": active, "sendMessage": sendMessageInterne})
                print("\nend running code from file script1.py\n")    
                print('STOP...')
                desactiveThymio()
                active[0] = False
                accumulator = ''
                state = 'IDLE'
                bluetoothManager.send_message('$STOPPED')
            except Exception as e:
                raise Exception("Error al ejecutar el código: {}".format(str(e)))

        # Create a new thread to run the code
        active[0] = True
        _thread.start_new_thread(run_code, ())
        print("Código ejecutado en segundo plano")
    except Exception as e:
        print(f"Error al crear el hilo para ejecutar el código: {str(e)}")
        raise Exception("Error al crear el hilo para ejecutar el código: {}".format(str(e)))

#--------------------------------------------------------------------------------------------
# stop: Function to stop the execution of the code
#--------------------------------------------------------------------------------------------
def stop():
    global active, state, accumulator 
    
    print('STOP...')
    desactiveThymio()
    active[0] = False
    accumulator = ''
    state = 'IDLE'
        

#--------------------------------------------------------------------------------------------
# reset: Function to reset the device
#--------------------------------------------------------------------------------------------
def reset():
    global bluetoothManager
    stop()
    bluetoothManager.send_message('$STOPPED')
    machine.reset()

#--------------------------------------------------------------------------------------------
# endReception: Function to be executed when the code is completely received
#--------------------------------------------------------------------------------------------
def endReception():
    global accumulator, state
    state = 'SAVING'
    
    print('END RECEIVING...')

#--------------------------------------------------------------------------------------------
# receiving: Function to be executed when the code is being received
#--------------------------------------------------------------------------------------------
def receiving(data):
    global accumulator

    print('RECEIVING...', data)
    if(data == '@EOF@'):
        accumulator += "\u000A"
    else:
        accumulator += data
        
#--------------------------------------------------------------------------------------------
# saving: Function to be executed when the code is being saved
#--------------------------------------------------------------------------------------------
def saving(data):
    global accumulator, state
    fileName = f'{data}.py'
    state = 'IDLE'
    
    try:
        with open(fileName, "w") as file:
            file.write(accumulator)
        print(f'codigo guardado en el archivo {fileName}', accumulator)
        accumulator = ''
    except Exception as e:
        print(f"Error al guardar el código en el archivo: {str(e)}") 
        
#--------------------------------------------------------------------------------------------
# receiving: Function to prepare the device to receive the code
#--------------------------------------------------------------------------------------------
def startReception():
    global accumulator, state
    
    print('START RECEIVING...')
    accumulator = "\u000A#Code\u000A"
    state = 'RECEIVING'
        
#--------------------------------------------------------------------------------------------
# desactiveThymio: Function to desactive Thymio (leds, motors and sound)
#--------------------------------------------------------------------------------------------
def desactiveThymio():
    mot = thymio.MOTORS()
    mot.set_speed(0, 0)
    for _i_ in range(8):
        led = thymio.LEDS_CIRCLE(_i_)
        led.off()

#--------------------------------------------------------------------------------------------
# handleReceivedMessage: Function to handle the messages received from the bluetooth
#--------------------------------------------------------------------------------------------
def handleReceivedMessage(data):
    global accumulator, state
    
    if (data == '$Desactive'):
        machine.reset()
    elif(data == '$Start') and state == 'IDLE':
        stop()
        time.sleep(1)
        startReception()
    elif(data == '$End'):
        endReception()
        bluetoothManager.send_message('$RECEIVED')
    elif(data == '$Run'):
        stop()
        time.sleep(1)
        running()
        bluetoothManager.send_message('$RUNNING')
    elif(data == '$Stop'):
        stop()
        bluetoothManager.send_message('$STOPPED')
    elif(data == '$Reset'):
        reset()
        bluetoothManager.send_message('$RESET')
    elif(state == 'RECEIVING'):
        receiving(data)
        bluetoothManager.send_message('$RECEIVING')
    elif(state == 'SAVING'):
        saving(data)
        bluetoothManager.send_message('$SAVING')
    else:
        print('ERROR: Invalid message')

bluetoothManager.set_on_message_received(handleReceivedMessage)