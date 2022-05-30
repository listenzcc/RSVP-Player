# %%
import cv2

from .logger import LOGGER
from .constants import CFG
from pathlib import Path

# %%
path = Path(CFG['videoFlow']['path'])

# %%


class VideoFlow(object):
    def __init__(self):
        self.capture = None
        LOGGER.info('Video flow initialized')
        pass

    def connect(self, path=path):
        if self.capture is not None:
            self.release()
        self.capture = cv2.VideoCapture(path.as_posix())
        self.count = 0
        LOGGER.info('Video flow connected')

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
        cv2.flip(frame, 1, frame)
        frame = frame.transpose([1, 0, 2])
        self.count += 1
        return frame


# %%
VIDEO_FLOW = VideoFlow()
VIDEO_FLOW.connect()

# %%
