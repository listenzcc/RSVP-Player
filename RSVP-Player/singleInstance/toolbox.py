# %%
import threading

from .logger import LOGGER
from .constants import *

# %%

size = (
    int(CFG['picture']['width']),
    int(CFG['picture']['height'])
)


def frame2surface(frame, size=size):
    surf = pygame.surfarray.make_surface(frame)
    surface = pygame.transform.scale(surf, size)
    return surface

# %%


class Pair(object):
    def __init__(self, frame, surface=None, idx=-1):
        self.frame = frame
        self.surface = surface
        self.idx = idx

        # The count is the counting of frame and surface
        # [1, 1] means the frame and surface are both ready
        # [1, 0] means the frame is ready, but the surface is not computed yet
        if surface is None:
            self.count = [1, 0]
        else:
            self.count = [1, 1]

        LOGGER.debug("Pair is initialized")

    def compute(self, size=size):
        t = threading.Thread(target=self._compute, args=(size,))
        t.setDaemon(True)
        t.start()

    def _compute(self, size):
        self.surface = frame2surface(self.frame, size)
        self.count[1] = 1
        LOGGER.debug('Computed surface by frame {}'.format(self.frame.shape))

# %%
