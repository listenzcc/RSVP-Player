# %%
import cv2
import numpy as np
import socket
import threading

# %%


def _pic_encoder(frame):
    '''
    Encode image into bytes, using .png format

    Args:
        - frame: The input frame, shape is (width, height, 3), dtype is uint8.

    Output:
        - bytes: The image coding bytes.
    '''
    assert(frame.dtype == np.uint8)
    assert(len(frame.shape) == 3)
    assert(frame.shape[2] == 3)

    success, arr = cv2.imencode('.png', frame)

    bytes = arr.tobytes()

    return bytes


picture_size = (800, 600, 3)


def mk_picture_package(uid=0, uid_length=16, n_length=64, byteorder='little'):
    frame = np.random.randint(0, 255, size=picture_size, dtype=np.uint8)

    frame[:100, :100, :] = 255

    frame_bytes = _pic_encoder(frame)

    n = len(frame_bytes)

    parts = [
        b'suspect',
        uid.to_bytes(uid_length, byteorder),
        n.to_bytes(n_length, byteorder),
        frame_bytes,
    ]

    return b''.join(parts)


# %%
# serverHost = '100.1.1.100'
serverHost = 'localhost'
serverPort = 9386

cmd_dict = dict(
    suspect=['command-suspect', '[S] Translate suspect picture'],
    close=['command-quit', '[Q] Quit'],
)


class TCPClient(object):
    def __init__(self):
        self.socket = socket.socket()
        self.uid = 1000
        pass

    def _listen(self):
        while True:
            try:
                print('<<', self.socket.recv(1024))
            except:
                print('Bye bye.')
                break

    def start(self):
        host = serverHost
        port = serverPort

        self.socket.connect((host, port))
        self.socket.send(b'Client sent hello.')

        t = threading.Thread(target=self._listen, args=())
        t.setDaemon(True)
        t.start()

        while True:
            inp = input('>> ')

            if inp == '':
                print(cmd_dict)
                continue

            if inp == 'q':
                break

            if inp == 's':
                self.socket.send(mk_picture_package(uid=self.uid))
                self.uid += 1
                continue

            self.socket.send(bytes(inp, 'utf8'))
            continue

        self.socket.close()


CLIENT = TCPClient()

# %%
if __name__ == '__main__':
    CLIENT.start()

# %%

# %%
