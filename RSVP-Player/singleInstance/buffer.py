# %%
import time
import socket
import random
import threading
import numpy as np

from .toolbox import _bytes, _pic_decoder, Pair

from .logger import LOGGER

from .constants import *

# %%
# Raw buffer


class RawBuffer(object):
    def __init__(self):
        self.limit = CFG['buffer']['maxSize']
        self.pairs = []

    def insert(self, pair):
        self.pairs.insert(0, pair)

    def append(self, pair):
        if pair is None:
            return
        self.pairs.append(pair)

    def refresh(self):
        self.valid = [e for e in self.pairs if e.count[1] == 1]
        self.frame_count = len(self.pairs)
        self.surface_count = len(self.valid)

# %%
# Non target buffer


class NonTargetBuffer(RawBuffer):
    def __init__(self):
        super(NonTargetBuffer, self).__init__()
        LOGGER.info('NonTargetBuffer initialized')
        pass

    def get_random(self, k=100):
        self.refresh()

        if self.surface_count == 0:
            LOGGER.error('NonTargetBuffer has no surface. Run CAPTURE first')
            return

        if k > self.surface_count:
            LOGGER.warning('NonTargetBuffer can not random_get enough surfaces, since {} > {}'.format(
                k, self.surface_count))
            LOGGER.warning(
                'NonTargetBuffer random_get is using choices with-replacement')
            return random.choices(self.valid, k=k)

        return random.sample(self.valid, k=k)

    def get_all(self):
        self.refresh()
        LOGGER.debug('NonTargetBuffer gives all the valid surfaces')
        return self.valid


NON_TARGET_BUFFER = NonTargetBuffer()

# %%
# Suspect buffer


class SuspectBuffer(RawBuffer):
    '''
    The pairs are sent from upper host
    '''

    def __init__(self):
        super(SuspectBuffer, self).__init__()
        LOGGER.info('SuspectBuffer initialized')
        pass

    def pop(self):
        self.refresh()

        if self.surface_count == 0:
            LOGGER.error(
                'SuspectBuffer can not pop, since the surface buffer is empty')
            return

        idx = self.valid[0].idx

        return self.pop_idx(idx)

    def pop_idx(self, idx):
        self.refresh()
        select = [e for e in self.valid if e.idx == idx]

        if len(select) == 0:
            LOGGER.error('SuspectBuffer can not find idx: {}'.format(idx))
            return

        if len(select) > 1:
            LOGGER.warning(
                'SuspectBuffer find {} pairs for idx: {}'.format(len(select), idx))

        LOGGER.debug('SuspectBuffer pop idx: {}'.format(idx))

        self._remove_idx(idx)

        return select

    def _remove_idx(self, idx):
        n = len(self.pairs)
        self.pairs = [e for e in self.pairs if not e.idx == idx]
        self.refresh()
        LOGGER.debug(
            'Pop idx: {}, size changes: {} -> {}'.format(idx, n, self.frame_count))


SUSPECT_BUFFER = SuspectBuffer()

# %%


class InterBuffer(RawBuffer):
    '''
    The pairs are considered to be finished.
    '''

    def __init__(self):
        super(InterBuffer, self).__init__()
        LOGGER.info('InterruptBuffer initialized')
        pass

    def pop(self):
        if len(self.pairs) == 0:
            LOGGER.error(
                'InterruptBuffer can not pop, since the pairs are empty')
            return

        first = self.pairs.pop(0)

        self.refresh()

        LOGGER.debug('InterruptBuffer pops 1 pairs')

        return first

    def _default(self):
        default_opt = 'DefaultOperation'
        while len(self.pairs) > 0:
            pair = self.pairs.pop(0)
            self.refresh()

            SUSPECT_BUFFER.pop_idx(pair.idx)
            SUSPECT_BUFFER.refresh()

            LOGGER.debug('Operation: {} to idx: {}'.format(
                default_opt, pair.idx))
            time.sleep(0.1)
        LOGGER.debug('Default operation stops.')
        pass

    def default(self):
        t = threading.Thread(target=self._default)
        t.setDaemon(True)
        t.start()
        LOGGER.debug('Default operation starts.')


INTER_BUFFER = InterBuffer()

# %%


def _append_frame(uid, body):
    frame = _pic_decoder(body)
    if frame is None:
        LOGGER.error('Can not decode body')
        return -1

    pair = Pair(frame, idx=uid)
    pair.compute()

    SUSPECT_BUFFER.append(pair)

    LOGGER.debug('SUSPECT_BUFFER appended')

    return 0


class IncomeClient(object):
    '''
    Handle the income TCP client.
    '''

    def __init__(self, client, addr):
        self.client = client
        self.addr = addr

        t = threading.Thread(target=self._hello, args=(), daemon=True)
        t.start()

        LOGGER.info('New client is received {}, {}'.format(client, addr))
        pass

    def _hello(self):
        self.client.send(_bytes(CFG['TCP']['welcomeMessage']))

        self.is_alive = True

        while True:
            try:
                recv = self.client.recv(1024)

                LOGGER.info('Receive {} from {}'.format(recv[:20], self.addr))

                # !!! Got suspect picture
                # 7: length of 'suspect'
                # 16: uid_length
                # 64: n_length
                # 100+: length of picture bytes
                if recv.startswith(b'suspect') and len(recv) > (7 + 16 + 64 + 100):
                    byteorder = 'little'
                    uid = int.from_bytes(recv[7:7+16], byteorder)
                    n_body = int.from_bytes(recv[7+16:7+16+64], byteorder)
                    body = recv[7+16+64:]
                    remain = n_body + 7+16+64 - len(recv)
                    LOGGER.debug('New suspect image received {}, {} | {}'.format(
                        uid, n_body-remain, n_body))

                    while remain > 0:
                        recv = self.client.recv(min(remain, 1024))
                        body += recv
                        remain -= len(recv)

                    if remain < 0:
                        LOGGER.error(
                            'Incorrect image translation, since remain < 0, {}'.format(remain))
                        continue

                    LOGGER.debug('Suspect image translation finished')

                    _append_frame(uid, body)

                    self.client.send(
                        _bytes('Got suspect frame: {}'.format(uid)))

                    continue

                self.client.send(_bytes('UnDo') + recv)

            except ConnectionResetError:
                LOGGER.error('Connection reset {}, {}'.format(
                    self.client, self.addr))
                break

            # if recv == b'':
            #     LOGGER.error('Connection closed {}, {}'.format(
            #         self.client, self.addr))
            #     break

            # print('<<', recv)

        self.client.close()

        self.is_alive = False

        pass


class TCPServer(object):
    '''
    TCP Server
    '''

    def __init__(self):
        self.bind()
        self.clients = []
        LOGGER.info('TCP initialized')
        pass

    def refresh(self):
        self.clients = [e for e in self.clients if e.is_alive]

    def bind(self):
        '''
        Bind the host:port
        '''
        self.socket = socket.socket()

        host = CFG['TCP']['host']
        port = int(CFG['TCP']['port'])

        self.socket.bind((host, port))

        LOGGER.info('TCP binds on {}:{}'.format(host, port))

    def serve(self):
        '''
        Start the serving
        '''
        t = threading.Thread(target=self.listen, args=(), daemon=True)
        t.start()

        LOGGER.info('TCP servers on {}'.format(self.socket))

        pass

    def listen(self):
        client_limit = int(CFG['TCP']['clientLimit'])
        self.socket.listen(client_limit)

        LOGGER.info('TCP listens: {}'.format(client_limit))

        # !!! It listens FOREVER
        # When new client connects,
        # it will be handled by the IncomeClient.
        while True:
            client, addr = self.socket.accept()
            LOGGER.debug('New client: {}: {}'.format(client, addr))
            client.send(_bytes(CFG['TCP']['welcomeMessage']))

            self.clients.append(IncomeClient(client, addr))

            pass


SERVER = TCPServer()

# %%


def summary_buffers():
    NON_TARGET_BUFFER.refresh()
    SUSPECT_BUFFER.refresh()
    INTER_BUFFER.refresh()
    SERVER.refresh()
    output = [
        '| Summary           {:4s}   {:4s} |'.format('', ''),
        '| Buffer Name     | {:4s} | {:4s} |'.format('frm', 'srf'),
        # Non target buffer
        '| NonTargetBuffer | {:4d} | {:4d} |'.format(
            NON_TARGET_BUFFER.frame_count, NON_TARGET_BUFFER.surface_count),
        # Suspect buffer
        '| SuspectBuffer   | {:4d} | {:4d} |'.format(
            SUSPECT_BUFFER.frame_count, SUSPECT_BUFFER.surface_count),
        # Interrupt buffer
        '| InterruptBuffer | {:4d} | {:4d} |'.format(
            INTER_BUFFER.frame_count, INTER_BUFFER.surface_count),
        # TCP connection
        '| TCPConnection   | {:4d} | {:4d} |'.format(
            len(SERVER.clients), 0
        )
    ]

    return output


# %%


def draw_summary():
    width = 1
    color = WHITE
    background = None
    antialias = True

    summary = summary_buffers()

    top = int(CFG['summaryRect']['top'])
    left = int(CFG['summaryRect']['left'])
    _top = 10

    for string in summary:
        text = FONT.render(string, antialias, color, background)
        rect = text.get_rect()
        # rect.height *= 1.1
        rect.center = (left + rect.width/2, top - rect.height / 2)
        top += _top + rect.height

        # SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)
        pygame.draw.rect(SCREEN, color, rect, width=width)

        pass

    return
