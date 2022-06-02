# %%
from .logger import LOGGER
from .loop_manager import LOOP_MANAGER

from .toolbox import Controller

from .buffer import INTER_BUFFER
from .buffer import SUSPECT_BUFFER
from .buffer import summary_buffers

from .constants import *

# %%

controllers = dict(
    MAIN=['__MAIN__', -1],
    ACCEPT=['__ACCEPT__', -1],
    DENY=['__DENY__', -1],
    IGNORE=['__IGNORE__', -1],
)

controller = Controller(controllers, title='Interaction')

# %%


def draw_summary():
    width = 1
    color = WHITE
    background = None
    antialias = True

    summary = summary_buffers()

    top = int(CFG['screen']['height']) / 2
    _top = 10
    w = int(CFG['screen']['width'])

    for string in summary:
        text = FONT.render(string, antialias, color, background)
        rect = text.get_rect()
        rect.height *= 1.1
        rect.center = (w - rect.width/2, top)
        top += _top + rect.height

        # SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)
        pygame.draw.rect(SCREEN, color, rect, width=width)

        pass

    return
# %%


def inter_loop():
    LOGGER.info('Inter loop started')

    pair = INTER_BUFFER.pop()
    if pair is None:
        LOGGER.error('Inter loop can not pop the inter buffer')
        LOOP_MANAGER.set('RSVP')
        return

    while True:
        if not LOOP_MANAGER.get() == 'INTER':
            LOGGER.info('Escape from inter loop')
            break

        SCREEN.fill(BLACK)
        controller.draw()

        position = (
            int(CFG['centerPatch']['left']),
            int(CFG['centerPatch']['top'])
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            escape = False
            cmd = controller.check(event)

            if cmd == 'MAIN':
                escape = True
                LOOP_MANAGER.set('MAIN')

                # Restore the INTER_BUFFER
                INTER_BUFFER.insert(pair)

                LOGGER.info(
                    'Inter loop receives cmd to enter into the MAIN loop'
                )

                pass

            if cmd == 'ACCEPT':
                escape = True
                LOOP_MANAGER.set('RSVP')
                LOGGER.info('Accept idx: {}'.format(pair.idx))
                SUSPECT_BUFFER.pop_idx(pair.idx)
                pass

            if cmd == 'DENY':
                escape = True
                LOOP_MANAGER.set('RSVP')
                LOGGER.info('Deny idx: {}'.format(pair.idx))
                SUSPECT_BUFFER.pop_idx(pair.idx)
                pass

            if cmd == 'IGNORE':
                escape = True
                LOOP_MANAGER.set('RSVP')
                LOGGER.info('Ignore idx: {}'.format(pair.idx))
                INTER_BUFFER.append(pair)
                pass

            if escape:
                LOGGER.info(
                    'Inter loop receives decision, escaping')
                return

        SCREEN.blit(pair.surface, position)
        draw_summary()
        pygame.display.flip()


# %%
