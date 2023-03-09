import socket
import os
import sys
ip = ""
port = 0
image = ""
"""
1. run with 3 arguments - ip, port, image
2. the image will be sent to the client
"""


def run_server(ip, port, image):
    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, int(port)))
    s.listen(1)
    print(f'ip is {ip}', f'port is {port}', f'image is {image}')
    while True:
        conn, addr = s.accept()
        print(f'connected to client on port: {port}')
        # listen for http get and return http response with image
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f'received: {data}')
            if data.startswith(b'GET'):
                with open(image, 'rb') as f:
                    conn.send(f.read())
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('INPUT IS NOT VALID - please enter 3 arguments')
        sys.exit(1)
    ip = sys.argv[1]
    port = sys.argv[2]
    image = sys.argv[3]
    # change dir to this file's dir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_server(ip, port, image)
