# %%
import base64
import socket
import struct
import json
from io import BytesIO

from PIL import Image

import numpy as np
import threading

# %%
from .toolbox import Pair
from .buffer import SUSPECT_BUFFER
from .logger import LOGGER
from .constants import *

# %%
host = CFG['Remote']['host']
port = int(CFG['Remote']['port'])
encoding = CFG['Remote']['encoding']

LOGGER.debug('Use cfg of Remote: {}, {}, {}'.format(host, port, encoding))

# %%


class RSVPSocket:
    def __init__(self, addr):
        self.addr = addr
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def build_connection(self):
        try:
            self.client.connect(self.addr)
        except Exception as e:
            print(e)
            self.build_connection()

    def send_message(self, msg: str):
        self.client.send(msg.encode(encoding))


# %%


def loop():
    client_socket = RSVPSocket((host, port))
    client_socket.build_connection()

    LOGGER.info('Remote suspect buffer client starts')
    while True:
        comm_type = client_socket.client.recv(2).decode()
        header = client_socket.client.recv(4)
        size = struct.unpack('i', header)
        recv_data = b""
        while len(recv_data) < size[0]:
            recv_data += client_socket.client.recv(size[0])
            print(len(recv_data))

        if comm_type == 'sm':
            UAV_info = recv_data[4:44]
            img_data = recv_data[44:]
            pack_id = struct.unpack('i', recv_data[:4])

            # path = folder.joinpath(img_id + '.jpg')
            # with open(path, 'wb') as jpg_file:
            #     jpg_file.write(img_data)
            # print('sm finished')

            fp = BytesIO(img_data)
            img = Image.open(fp)
            mat = np.array(img)
            LOGGER.debug('sm recv: {}'.format(mat.shape, mat.dtype, img_id))

            pair = Pair(mat, idx=1000+int(img_id))
            pair.compute()
            SUSPECT_BUFFER.append(pair)

            client_socket.send_message('sm finished')

        if comm_type == 'js':
            json_data = json.loads(recv_data.decode())
            img_base64_str = json_data.get("Img")
            img_data = base64.b64decode(img_base64_str)
            img_id = json_data.get("PackID")

            # path = folder.joinpath(img_id + '.jpg')
            # with open(path, 'wb') as jpg_file:
            #     jpg_file.write(img_data)
            # print('js finished')

            fp = BytesIO(img_data)
            img = Image.open(fp)
            mat = np.array(img)
            LOGGER.debug('js recv: {}'.format(mat.shape, mat.dtype, img_id))

            pair = Pair(mat, idx=1000+int(img_id))
            pair.compute()
            SUSPECT_BUFFER.append(pair)

            client_socket.send_message('js finished')


def _loop():
    while True:
        try:
            loop()
        except Exception as err:
            LOGGER.error(err)
        LOGGER.debug('Next')


# %%
t = threading.Thread(target=_loop)

t.setDaemon(True)
t.start()

# %%
