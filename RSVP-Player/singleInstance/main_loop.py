from .logger import LOGGER
from .loop_manager import LOOP_MANAGER
from .constants import *


def draw_controllers():
    width = 3
    color = WHITE
    background = None
    antialias = True

    top = int(CFG['screen']['height']) / 10
    _top = int(CFG['screen']['height']) / 10
    left = int(CFG['screen']['width']) / 2

    controllers = dict(
        INTER=['__INTER__', -1],
        RSVP=['__RSVP__', -1],
    )

    for j, cmd in enumerate(controllers):
        string = controllers[cmd][0]
        text = FONT.render(string, antialias, color, background)
        rect = text.get_rect()
        rect.height *= 1.1
        rect.center = (left, top)
        top += _top

        SCREEN.fill(BLACK, rect)
        SCREEN.blit(text, rect)
        pygame.draw.rect(SCREEN, color, rect, width=width)

        controllers[cmd][1] = rect

    return controllers


def main_loop():
    controllers = draw_controllers()
    while True:
        SCREEN.fill(BLACK)
        draw_controllers()
        pygame.display.flip()

        if not LOOP_MANAGER.get() == 'MAIN':
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            if event.type == pygame.MOUSEBUTTONUP:
                for cmd in controllers:
                    if controllers[cmd][1].contains(event.pos, (1, 1)):
                        LOGGER.info('Event: MouseButtonDown: {}'.format(cmd))
