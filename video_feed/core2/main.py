import urequests
import M5


UNITV2_IP = "192.168.1.114"


def parse_multipart_stream(response, boundary):
    buffer = bytearray()
    while True:
        chunk = response.raw.read(4096)  # Read chunks from the response
        if not chunk:
            break

        buffer.extend(chunk)
        while True:
            # Find the boundary in the buffer
            boundary_index = buffer.find(b'--' + boundary.encode())
            if boundary_index == -1:
                # Boundary not found - get more data
                break

            # Skip the boundary and headers
            end_of_headers = buffer.find(b'\r\n\r\n', boundary_index)
            if end_of_headers == -1:
                break

            # Extract the frame
            start_of_frame = end_of_headers + 4
            end_of_boundary = buffer.find(b'--' + boundary.encode(), start_of_frame)
            if end_of_boundary == -1:
                break

            frame_data = buffer[start_of_frame:end_of_boundary]
            buffer = buffer[end_of_boundary:]

            yield frame_data

def fetch_and_display_stream(url, boundary):
    # Connect to the video feed
    response = urequests.get(url, stream=True)

    try:
        for frame_data in parse_multipart_stream(response, boundary):
            # Display the image on LCD
            M5.Lcd.drawImage(frame_data)
    
    finally:
        response.close()


if __name__ == "__main__":

    M5.begin()

    fetch_and_display_stream(url=f'http://{UNITV2_IP}/video_feed', boundary='frame')
