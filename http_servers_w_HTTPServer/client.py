from PIL import Image
from io import BytesIO
import requests
import sys
url = 'http://localhost:!!!port number here!!!}'
"""
1. run with 1 argument - the port number
2. the image will be shown
"""


def send_request(url):
    response = requests.get(url)
    return response.content


def show_image(img_data):
    img = Image.open(BytesIO(img_data))
    img.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('INPUT IS NOT VALID - please enter 1 argument')
        sys.exit(1)
    url = f'http://localhost:{sys.argv[1]}'
    response = send_request(url)
    show_image(response)
