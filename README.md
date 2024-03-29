# Thymio3-IoT

A repository for different projects integrating [M5Stack](https://m5stack.com/) IoT devices with Thymio3:

- [Person Tracking](#person-tracking)
- [Remote Control](#remote-control)


## Global Setup

### Tools

To upload the firmware on the devices we used the command line tool [ampy](https://github.com/scientifichackers/ampy) which can easily be installed with:

```bash
pip3 install adafruit-ampy
```

If you want to access the devices serial port for debugging or using Micropython REPL, you can install a terminal emulation program. On Ubuntu you can use **picocom** which can be installed on with:

```bash
sudo apt-get install picocom
```

**Note:** *These are personal choices. You may use any tool of your choice for uploading firmware or serial port debugging.*


### Core2 Setup
1. Follow [M5Stack's instructions](https://docs.m5stack.com/en/quick_start/core2/mpy) to install the required drivers as well as the burning tool.

2. Open **M5Burner** app and select **CORE2 & TOUGH** then download **UIFlow2.0** version of your choice (tested until Alpha-29).

3. Connect the Core2 to your computer, press the **Burn** button and follow the instructions.


### MQTT and Wi-Fi Setup

In order to communicate between the devices, we chose the [MQTT](https://mqtt.org/) messaging protocol.
In this project we used [mosquitto](https://mosquitto.org/) to launch a local MQTT broker on our computer.

Once your broker is setup, you can follow the folowing instructions:

1. Update the `MQTT_BROKER` variable in ***common/config.py*** with your computer ip address.

2. Save your wifi credentials in ***common/wifi.py***.


## Person Tracking


![Person Tracking Demonstrator](docs/images/tracking_pic_resized.jpg)

This project makes use of the **Face Detector** feature of the M5Stack UnitV2 AI camera and enables Thymio3 to track and follow a person face.

This project requires the following devices:
- Thymio3
- [M5Stack Core2](https://shop.m5stack.com/products/m5stack-core2-esp32-iot-development-kit) x2
- [M5Stack UnitV2](https://shop.m5stack.com/products/unitv2-ai-camera-gc2145)

### Installation

Make sure both Core2 are setup according to [Core2 Setup](#core2-setup).

#### On-board Core2

Connect the first Core2 to your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py
ampy put boot.py
ampy put img

cd ../person_tracking/on_board_core2/
ampy put eyes.py
ampy put unitV2.py
ampy put main.py
```

#### Remote Core2

Connect the second Core2 to your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py
ampy put boot.py
ampy put img

cd ../person_tracking/remote_core2/
ampy put main.py
```

#### Thymio3

Connect the Thymio3 to your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py

cd ../person_tracking/thymio/
ampy put boot.py
ampy put main.py
```

#### UnitV2

1. Follow the [M5Stack  documentation](https://docs.m5stack.com/en/quick_start/unitv2/config) for setting up SSH and Wi-Fi for the UnitV2.

2. Update the following files to the device via ssh:

```bash
scp /path/to/Thymio3-IoT/person_tracking/unitV2/server_core.py \
root@UNITV2_IP_ADDRESS:/home/m5stack/payload/server_core.py

scp /path/to/Thymio3-IoT/person_tracking/unitV2/bin/face_detector \
root@UNITV2_IP_ADDRESS:/home/m5stack/payload/bin/face_detector
```

The new firmware will be used when the UnitV2 server is restarted (press 5s on the button at the top of the device).

To compile other function binaries, see [my UnitV2Framework fork](https://github.com/Constantin-dcx/UnitV2Framework).

**Note:** *You may need to remove the existing file from the device before uploading the new one to prevent corrupting it when using **scp**.*


## Remote Control

![Person Tracking Demonstrator](docs/images/remote_pic_resized.jpg)

This project relies on a remote to control the Thymio3 speed and open an on-board gripper.

This project requires the following devices:
- Thymio3
- [M5Stack Core2](https://shop.m5stack.com/products/m5stack-core2-esp32-iot-development-kit) x2
- [M5Stack DinBase](https://docs.m5stack.com/en/base/DIN%20BASE)
- [M5Stack Catch Unit](https://shop.m5stack.com/products/catch-unit)

### Installation

Make sure both Core2 are setup according to [Core2 Setup](#core2-setup).

#### On-board Core2

Connect the DinBase module to the bottom of the first Core2, then plug it into your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py
ampy put boot.py
ampy put img

cd ../remote_control/on_board_core2/
ampy put catch_unit.py
ampy put main.py
```

#### Remote Core2

Connect the second Core2 to your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py
ampy put boot.py
ampy put img

cd ../remote_control/remote_core2/
ampy put main.py
```

#### Thymio3

Connect the Thymio3 to your computer and upload the following files to it:

```bash
export AMPY_PORT=/dev/ttyACM0  # Change to your actual port

cd common/
ampy put wifi.py
ampy put config.py

cd ../remote_control/thymio/
ampy put boot.py
ampy put main.py
```