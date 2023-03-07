from PIL import Image
from io import BytesIO
import sys
import socket

serv = 'http://localhost:30001'


def send_request():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = serv.split('//')[1].split(':')[0]
    port = int(serv.split(':')[-1])
    s.connect((host, port))
    # send http get request
    s.send(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
    # receive all image data
    data = b''
    while True:
        part = s.recv(1024)
        data += part
        if len(part) < 1024:
            break
    s.close()
    return data


def show_image(img_data):
    img = Image.open(BytesIO(img_data))
    img.show()


if __name__ == "__main__":
    response = send_request()
    print(f'got {len(response)} bytes')
    show_image(response)
