import sys
import camera
from machine import Pin

import wifi

wifi.connect(True)

CAMERA_IP = "192.168.1.102"

try:
	camera.init(0,format=camera.GRAYSCALE,framesize=camera.FRAME_96X96,sioc=23,siod=25,xclk=27,vsync=22,href=26,pclk=21,d0=32,d1=35,d2=34,d3=5,d4=39,d5=18,d6=36,d7=19,reset=15)
except:
	print("Error when initializing the camera")
	sys.exit()

# initialize the flash-light LED, it is connected to GPIO 4
flash_light = Pin(2,Pin.OUT)
# switch it off
flash_light.off()


import urequests

img = camera.capture()
if not img:
    print("Capture Failed :'(")
	

FILE_PATH = "captured_image.jpg"

# img.save(FILE_PATH)
urequests.request("POST", f"{CAMERA_IP}:80/upload", files={"file": (FILE_PATH, img)})












# # Set up a basic HTTP server

# import usocket as socket

# def handle_request(client_socket):

#     print("received request")

#     flash_light.on()

#     request_data = client_socket.recv(1024)
#     request_lines = request_data.decode("utf-8").split("\r\n")

#     # Assuming the image capture should be triggered when "/capture" is accessed
#     if "/capture" in request_lines[0]:
#         # Capture image using ESP32 Cam
#         img = camera.capture()

#         if not img:
#             print("Capture Failed :'(")

#         print(img)

#         # Send HTTP response headers
#         client_socket.send("HTTP/1.1 200 OK\r\n")
#         client_socket.send("Content-Type: image/jpeg\r\n")
#         client_socket.send("Connection: close\r\n\r\n")

#         # Send the captured image
#         client_socket.send(img)

#         print("sent")

#     print("finished")

#     client_socket.close()

# # Set up the server socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('', 80))
# server_socket.listen(5)

# print("Server listening on port 80")

# i=0
# while True:
#     client_socket, addr = server_socket.accept()
#     handle_request(client_socket)

#     i = i + 1
#     print(i)