from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys
# HOST = 'localhost'
# PORT = 30001
ip = ""
port = 0
image = ""
"""
1. run with 3 arguments - ip, port, image
2. the image will be sent to the client
"""


class MyHandler(BaseHTTPRequestHandler):
    # return cat image
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        with open(image, 'rb') as f:
            self.wfile.write(f.read())


def run_server(ip, port, image):
    server = HTTPServer((ip, int(port)), MyHandler)
    print(f'ip is {ip}', f'port is {port}', f'image is {image}')
    server.serve_forever()


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

    print(f'server is running on {ip}:{port}')
