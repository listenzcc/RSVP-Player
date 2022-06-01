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


class Controller(object):
    def __init__(self, controllers, title='none'):
        self.controllers = controllers
        self.title = title
        self.draw()
        LOGGER.debug('Controller initialized: {}, {}'.format(
            title, controllers))

    def check(self, event):
        '''
        Check the clicked controller
        '''
        # Only accept MOUSEBUTTONUP
        if not event.type == pygame.MOUSEBUTTONUP:
            return

        controllers = self.controllers
        for cmd in controllers:
            if controllers[cmd][1].contains(event.pos, (1, 1)):
                LOGGER.debug('Detect click event on cmd: {}'.format(cmd))
                return cmd

        return

    def draw(self):
        '''
        Draw controllers into the pygame window

        The example is

        controllers = dict(
            MAIN=['__MAIN__', -1],
            CAPTURE=['__CAPTURE__', -1],
        )

        They are drawn in the top of the window from left to right.

        -------------------------
        | c1  c2  c3 ...        |
        |                       |
        |                       |
        |                       |
        |                       |
        -------------------------

        '''
        controllers = self.controllers
        title = self.title

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
        top = 30
        left = int(CFG['screen']['width']) - rect.width
        rect.center = (left, top)

        SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)

        # Draw controllers
        width = 1
        color = WHITE
        background = None
        antialias = True

        top = 30
        left = int(CFG['screen']['width']) / 10
        _left = 30

        for j, cmd in enumerate(controllers):
            string = controllers[cmd][0]
            text = FONT.render(string, antialias, color, background)
            rect = text.get_rect()
            rect.height *= 1.1
            rect.center = (left, top)
            left += _left + rect.width

            SCREEN.fill(BLACK, rect)
            SCREEN.blit(text, rect)
            pygame.draw.rect(SCREEN, color, rect, width=width)

            controllers[cmd][1] = rect

        self.controllers = controllers

        return controllers


def draw_controllers(controllers, title='none'):
    '''
    Draw controllers into the pygame window

    The example is

    controllers = dict(
        MAIN=['__MAIN__', -1],
        CAPTURE=['__CAPTURE__', -1],
    )

    They are drawn in the top of the window from left to right.

    -------------------------
    | c1  c2  c3 ...        |
    |                       |
    |                       |
    |                       |
    |                       |
    -------------------------

    '''
    # Draw title
    width = 1
    color = YELLOW
    background = None
    antialias = True

    text = FONT.render(title, antialias, color, background)
    rect = text.get_rect()
    rect.height *= 1.1
    rect.width *= 1.5
    top = 30
    left = int(CFG['screen']['width']) - rect.width
    rect.center = (left, top)

    SCREEN.fill(BLACK, rect)
    SCREEN.blit(text, rect)

    # Draw controllers
    width = 1
    color = WHITE
    background = None
    antialias = True

    top = 30
    left = int(CFG['screen']['width']) / 10
    _left = 30

    for j, cmd in enumerate(controllers):
        string = controllers[cmd][0]
        text = FONT.render(string, antialias, color, background)
        rect = text.get_rect()
        rect.height *= 1.1
        rect.center = (left, top)
        left += _left + rect.width

        SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)
        pygame.draw.rect(SCREEN, color, rect, width=width)

        controllers[cmd][1] = rect

    return controllers

# %%
