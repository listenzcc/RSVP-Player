# %%
import base64
import socket
import threading
import struct
import time
from io import BytesIO
from PIL import Image
from json import dumps

# %%
IP = '127.0.0.1'
PORT = 9999

ENCODING = 'utf-8'

# %%
img = Image.open('240.jpg')

# %%


def pil2bytes(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG', quality=95)
    byte_data = img_buffer.getvalue()
    return byte_data


def pil2str(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG', quality=95)
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    str_data = base64_str.decode(ENCODING)
    return str_data


class AISocket:
    def __init__(self, addr):
        self.addr = addr
        self.server = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.client_socket = None
        self.client_addr = None

    def listen(self):
        self.server.bind(self.addr)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(2)
        while True:
            print('start listen')
            self.client_socket, self.client_addr = self.server.accept()
            print(self.client_socket)
            print(self.client_addr)
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            recv_data = self.client_socket.recv(1024)
            if recv_data.decode() == 'sm finished':
                print(recv_data)
                t2 = time.time()
                print('data packed:{}ms'.format((t2 - t1) * 1000))
            if recv_data.decode() == 'js finished':
                t2 = time.time()
                print('data packed:{}ms'.format((t2 - t1) * 1000))

    def send_socket_message(self, data):
        self.client_socket.send('sm'.encode())
        size = len(data)
        pack_header = struct.pack('i', size)
        self.client_socket.send(pack_header)
        self.client_socket.send(data)

    def send_json(self, data):
        self.client_socket.send('js'.encode())
        size = len(data)
        pack_header = struct.pack('i', size)
        self.client_socket.send(pack_header)
        self.client_socket.send(data)


ai_socket = AISocket((IP, PORT))
threading.Thread(target=ai_socket.listen, daemon=True).start()
# ai_socket.run()


def socket_comm(pack_id):
    global t1
    while True:
        input()

        t1 = time.time()

        img_bytes = pil2bytes(img)
        id_byte = struct.pack('i', pack_id)
        uav_data = bytes.fromhex('0000000000000000') + bytes.fromhex('0000000000000000') \
            + bytes.fromhex('00000000') + bytes.fromhex('00000000') + bytes.fromhex('be79cd1b') \
            + bytes.fromhex('3ee77001') + \
            bytes.fromhex('00000000') + bytes.fromhex('3fd920e7')
        load_data = id_byte + uav_data + img_bytes
        pack_id += 1
        print(pack_id)
        ai_socket.send_socket_message(load_data)


def json_cmm(pack_id):
    global t1
    while True:
        input('Enter to send a picture')
        t1 = time.time()
        img_str = pil2str(img)
        json_data = {}

        json_data["PackID"] = str(pack_id)
        json_data["Lat"] = "0000000000000000"
        json_data["Lon"] = "0000000000000000"
        json_data["X"] = "00000000"
        json_data["y"] = "00000000"
        json_data["Roll"] = "be79cd1b"
        json_data["Pitch"] = "3ee77001"
        json_data["Height"] = "00000000"
        json_data["Yaw"] = "3fd920e7"
        json_data["Img"] = img_str

        json_data = dumps(json_data, indent=2)
        pack_id += 1
        ai_socket.send_json(bytes(json_data.encode(ENCODING)))


if __name__ == '__main__':
    p_id = 0

    # 20ms
    # socket直接通信
    # socket_comm(p_id)

    # 35ms
    # socket Json通信
    json_cmm(p_id)
