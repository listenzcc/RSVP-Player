# %%
import cv2

import os

from .logger import LOGGER
from .constants import CFG
from pathlib import Path

# %%
# path = Path(CFG['videoFlow']['path'])

# path = Path(os.environ.get('HOME'), 'videos', 'video.mp4')

if os.environ.get('HOME', None) is None:
    LOGGER.warning('HOME environment variable is not set, try to set it with HOMEPATH')
    os.environ['HOME'] = os.environ.get('HOMEPATH', None)
    if os.environ.get('HOME') is None:
        LOGGER.error('HOME environment variable is not set, please set it manually')

LOGGER.info('HOME environment variable is {}'.format(os.environ.get('HOME')))

known_path = dict()
for e in CFG['videoFlow']:
    known_path[e] = CFG['videoFlow'][e]
LOGGER.info('Found video flows: {}'.format(known_path))

# %%


class VideoFlow(object):
    def __init__(self):
        self.capture = None
        LOGGER.info('Video flow initialized')
        pass

    def connect(self, name='video'):
        # ! It is a dangerous method
        # ! We will find path for know_path,
        # ! if fails, the name will be used.

        self.name = '{}'.format(name)

        path = known_path.get(name, name)

        # Convert the path into string
        if isinstance(path, Path):
            path = path.as_posix()

        if self.capture is not None:
            self.release()
        self.capture = cv2.VideoCapture(path)
        self.count = 0
        LOGGER.info('Video flow connected to name:{}'.format(name))

    def release(self):
        self.capture.release()
        self.capture = None
        LOGGER.info('Video flow closed')

    def get(self):
        if self.capture is None:
            LOGGER.error('Video flow is not connected')
            return

        success, frame = self.capture.read()

        if not success:
            LOGGER.error('Can not read capture.')
            return

        # Convert BGR2RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Flip
        # cv2.flip(frame, 1, frame)
        frame = frame.transpose([1, 0, 2])
        self.count += 1
        return frame


# %%
VIDEO_FLOW = VideoFlow()
VIDEO_FLOW.connect()

# %%
