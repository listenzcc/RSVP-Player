# %%
from .logger import LOGGER
from .loop_manager import LOOP_MANAGER
from .toggle_options import TOGGLE_OPTION
from .buffer import draw_summary

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
        TOGGLE_OPTION.draw()
        controller.draw(draw_patches=True)

        if not LOOP_MANAGER.get() == 'MAIN':
            LOGGER.info('Escape from main loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            cmd = controller.check(event)
            TOGGLE_OPTION.check(event)

            if cmd == 'CAPTURE':
                LOOP_MANAGER.set('CAPTURE')

            if cmd == 'RSVP':
                LOOP_MANAGER.set('RSVP')

        if TOGGLE_OPTION.options['SUM'][2]:
            draw_summary()

        pygame.display.flip()

# %%
