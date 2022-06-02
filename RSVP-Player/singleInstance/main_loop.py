# %%
from .logger import LOGGER
from .loop_manager import LOOP_MANAGER

from .toolbox import Controller

from .constants import *

# %%


controllers = dict(
    CAPTURE=['__CAPTURE__', -1],
    RSVP=['__RSVP__', -1],
)

controller = Controller(controllers, title='Main')


# %%
def main_loop():
    LOGGER.info('Main loop started')
    while True:
        SCREEN.fill(BLACK)
        controller.draw()
        pygame.display.flip()

        if not LOOP_MANAGER.get() == 'MAIN':
            LOGGER.info('Escape from main loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            cmd = controller.check(event)

            if cmd == 'CAPTURE':
                LOOP_MANAGER.set('CAPTURE')

            if cmd == 'RSVP':
                LOOP_MANAGER.set('RSVP')

# %%
