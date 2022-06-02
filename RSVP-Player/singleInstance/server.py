# # %%
# import socket
# import threading

# from .logger import LOGGER
# from .toolbox import _bytes, _pic_decoder
# from .buffer import SUSPECT_BUFFER
# from .constants import *

# # %%


# class IncomeClient(object):
#     '''
#     Handle the income TCP client.
#     '''

#     def __init__(self, client, addr):
#         self.client = client
#         self.addr = addr

#         t = threading.Thread(target=self._hello, args=(), daemon=True)
#         t.start()

#         LOGGER.info('New client is received {}, {}'.format(client, addr))
#         pass

#     def _hello(self):
#         self.client.send(_bytes(CFG['TCP']['welcomeMessage']))

#         self.is_alive = True

#         while True:
#             try:
#                 recv = self.client.recv(1024)

#                 LOGGER.info('Receive {} from {}'.format(recv, self.addr))

#                 self.client.send(_bytes('UnDo') + recv)

#             except ConnectionResetError:
#                 LOGGER.error('Connection reset {}, {}'.format(
#                     self.client, self.addr))
#                 break

#             # if recv == b'':
#             #     LOGGER.error('Connection closed {}, {}'.format(
#             #         self.client, self.addr))
#             #     break

#             # print('<<', recv)

#         self.client.close()

#         self.is_alive = False

#         pass


# # %%
# class TCPServer(object):
#     '''
#     TCP Server
#     '''

#     def __init__(self):
#         self.bind()
#         self.clients = []
#         LOGGER.info('TCP initialized')
#         pass

#     def refresh(self):
#         self.clients = [e for e in self.clients if e.is_alive]

#     def bind(self):
#         '''
#         Bind the host:port
#         '''
#         self.socket = socket.socket()

#         host = CFG['TCP']['host']
#         port = int(CFG['TCP']['port'])

#         self.socket.bind((host, port))

#         LOGGER.info('TCP binds on {}:{}'.format(host, port))

#     def serve(self):
#         '''
#         Start the serving
#         '''
#         t = threading.Thread(target=self.listen, args=(), daemon=True)
#         t.start()

#         LOGGER.info('TCP servers on {}'.format(self.socket))

#         pass

#     def listen(self):
#         client_limit = int(CFG['TCP']['clientLimit'])
#         self.socket.listen(client_limit)

#         LOGGER.info('TCP listens: {}'.format(client_limit))

#         # !!! It listens FOREVER
#         # When new client connects,
#         # it will be handled by the IncomeClient.
#         while True:
#             client, addr = self.socket.accept()
#             LOGGER.debug('New client: {}: {}'.format(client, addr))
#             client.send(_bytes(CFG['TCP']['welcomeMessage']))

#             self.clients.append(IncomeClient(client, addr))

#             pass


# # %%
# SERVER = TCPServer()

# # %%
