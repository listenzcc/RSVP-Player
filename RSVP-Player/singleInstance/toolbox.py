# %%
import cv2
import numpy as np
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


class Controller(object):
    def __init__(self, controllers, title='none'):
        self.controllers = controllers
        self.title = title
        self.mouse_over = ''
        self.draw()
        LOGGER.debug('Controller initialized: {}, {}'.format(
            title, controllers))

    def check(self, event):
        '''
        Check the clicked controller
        '''
        # Deal with mouse_over events
        if event.type == pygame.MOUSEMOTION:
            self.mouse_over = ''
            controllers = self.controllers
            for cmd in controllers:
                if controllers[cmd][1].contains(event.pos, (1, 1)):
                    self.mouse_over = cmd
                    break

        # Only accept MOUSEBUTTONUP
        if not event.type == pygame.MOUSEBUTTONUP:
            return

        controllers = self.controllers
        for cmd in controllers:
            if controllers[cmd][1].contains(event.pos, (1, 1)):
                LOGGER.debug('Detect click event on cmd: {}'.format(cmd))
                return cmd

        return

    def draw(self, draw_patches=False):
        '''
        Draw controllers into the pygame window

        The example is

        controllers = dict(
            MAIN=['__MAIN__', -1],
            CAPTURE=['__CAPTURE__', -1],
        )

        They are drawn in the north west corner of the window from left to right.
        Moreover, the title will be drawn in the north east corner of the window.

        -------------------------
        | c1  c2  c3 ...  Title |
        |                       |
        |                       |
        |                       |
        |                       |
        -------------------------

        '''

        controllers = self.controllers
        title = self.title

        if draw_patches:
            # Draw rect stroke of picture patches
            width = 1
            background = None
            antialias = True

            # Left patch
            color = GREEN
            top = int(CFG['centerPatch']['top'])
            left = int(CFG['centerPatch']['left'])
            rect = (left, top, size[0], size[1])
            pygame.draw.rect(SCREEN, REAL_BLACK, rect)
            pygame.draw.rect(SCREEN, color, rect, width=width)

            string = 'Patch-1'
            text = FONT.render(string, antialias, color, background)
            rect = text.get_rect()
            rect.height *= 1.1
            rect.center = (left + rect.width/2 + FONT_SIZE,
                        top+rect.height/2 + FONT_SIZE)
            SCREEN.blit(text, rect)

            # Right patch
            if CFG['RSVP']['mode'] == 'dual':
                color = CYAN
                top = int(CFG['subPatch']['top'])
                left = int(CFG['subPatch']['left'])
                rect = (left, top, size[0], size[1])
                pygame.draw.rect(SCREEN, REAL_BLACK, rect)
                pygame.draw.rect(SCREEN, color, rect, width=width)

                string = 'Patch-2'
                text = FONT.render(string, antialias, color, background)
                rect = text.get_rect()
                rect.height *= 1.1
                rect.center = (left + rect.width/2 + FONT_SIZE,
                            top+rect.height/2 + FONT_SIZE)
                SCREEN.blit(text, rect)

        # Draw title
        width = 1
        color = YELLOW
        background = None
        antialias = True

        title = controllers.get('_TITLE', title)

        text = FONT.render(title, antialias, color, background)
        rect = text.get_rect()
        rect.height *= 1.1
        rect.width *= 1.5
        top = int(CFG['cmdTitle']['top'])
        left = int(CFG['cmdTitle']['left'])
        rect.center = (left, top)

        SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)

        # Draw controllers
        width = 1
        background = None
        antialias = True

        top = int(CFG['cmdBar']['top'])
        left = int(CFG['cmdBar']['left'])
        _left = 30

        for j, cmd in enumerate(controllers):
            if cmd == self.mouse_over:
                color = YELLOW
            else:
                color = WHITE

            string = controllers[cmd][0]
            text = FONT.render(string, antialias, color, background)
            rect = text.get_rect()
            rect.height *= 1.1
            rect.center = (left, top)
            left += _left + rect.width + 20

            SCREEN.fill(BLACK, rect)
            SCREEN.blit(text, rect)

            pygame.draw.rect(SCREEN, color, rect, width=width)

            controllers[cmd][1] = rect

        self.controllers = controllers

        return controllers


# %%


def _bytes(string, coding=CFG['TCP']['coding']):
    '''
    Code the string into bytes

    Args:
        - buf: The input buf, if it is string, it will be converted to bytes; if it is bytes, it will be left no changed.
        - coding: The coding to use, it has default value.

    Output:
        Return the bytes of coding.
    '''
    return bytes(string, coding)

# %%


def _pic_encoder(img):
    '''
    Encode image into bytes, using .png format

    Args:
        - img: The input image, shape is (width, height, 3), dtype is uint8.

    Output:
        - bytes: The image coding bytes.
    '''
    assert(img.dtype == np.uint8)
    assert(len(img.shape) == 3)
    assert(img.shape[2] == 3)

    success, arr = cv2.imencode('.png', img)

    bytes = arr.tobytes()

    return bytes

# %%


def _pic_decoder(bytes):
    '''
    Decode image from bytes, using default method

    Args:
        - bytes: The bytes to decode.

    Output:
        - img: The decoded image, shape is (width, height, 3), dtype is uint8.
        - Return None if it fails on decoding.
    '''
    assert(isinstance(bytes, type(b'a')))

    try:
        arr = np.frombuffer(bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except:
        LOGGER.error('Image decode failed')
        return None

    return img

# %%
