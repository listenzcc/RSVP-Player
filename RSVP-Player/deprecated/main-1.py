# %%
import time
from random import randint

from startup import LOGGER
from state import STATE
from constants import *

# %%
screen = pygame.display.set_mode(MODE)
pygame.display.set_caption(CAPTION)

# %%


def wait_event(timeout=TIMEOUT):
    event = pygame.event.wait(timeout)

    if event.type == pygame.NOEVENT:
        LOGGER.debug('No event received in {} milliseconds'.format(timeout))

    return event


def clear_screen():
    screen.fill(BLACK)
    pass

# %%


def draw_message(messages):
    antialias = True
    color = (200, 200, 0)
    background = (10, 10, 100)
    background = None
    padding = 2

    height = 0
    for j, message in enumerate(messages):
        string = '{}. {}'.format(j, message)
        string = '{:30s}'.format(string)

        text = FONT.render(string,
                           antialias, color, background)
        textRect = text.get_rect()
        textRect.center = (
            int(CFG['messagePatch']['left']),
            int(CFG['messagePatch']['top']) + height,
        )
        height += textRect.height + padding
        text.set_alpha(100)
        screen.fill(BLACK, textRect)
        screen.blit(text, textRect)


# %%
def draw_controllers():
    width = 3
    color = GRAY
    background = None
    antialias = True

    top = 30
    left = 100
    _left = 200

    controllers = dict(
        INTER=['__INTER__', -1],
        RSVP=['__RSVP__', -1],
        CLEAR=['__CLEAR__', -1]
    )

    for j, cmd in enumerate(controllers):
        string = controllers[cmd][0]
        text = FONT.render(string, antialias, color, background)
        rect = text.get_rect()
        rect.height *= 1.1
        rect.center = (left, top)
        left += _left

        screen.fill(BLACK, rect)
        screen.blit(text, rect)
        pygame.draw.rect(screen, color, rect, width=width)

        controllers[cmd][1] = rect

    return controllers


controllers = draw_controllers()

# %%

# %%
clock = pygame.time.Clock()
clear_screen()
pygame.display.flip()

STATE.set('INTER')

chunk_count = 100
chunk_idx = 0

while True:
    if STATE.get() == 'INTER':
        event = wait_event()

        if event.type == pygame.QUIT:
            QUIT_PYGAME()

        if event.type == pygame.MOUSEBUTTONDOWN:
            print('MOUSEBUTTONDOWN', event.pos)
            mx, my = event.pos
            pygame.draw.circle(screen, (255, 255, 0), (mx, my), 50)

            for cmd in controllers:
                print(cmd)
                if controllers[cmd][1].contains(event.pos, (1, 1)):
                    LOGGER.info('Event: MouseButtonDown: {}'.format(cmd))
                    if cmd == 'CLEAR':
                        clear_screen()

                    if cmd == 'RSVP':
                        STATE.set(cmd)
                        chunk_idx = 0
                        clear_screen()

                    if cmd == 'INTER':
                        STATE.set(cmd)

                    break

        if event.type == pygame.MOUSEBUTTONUP:
            print('MOUSEBUTTONUP')
            pass

        if event.type == pygame.MOUSEMOTION:
            # print('MOUSEMOTION')
            mx, my = event.pos
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            pygame.draw.circle(screen, (r, g, b,), (mx, my), 50)

        draw_message(STATE.queue)
        draw_controllers()
        pygame.display.flip()

    else:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

        if not chunk_idx < chunk_count:
            STATE.set('INTER')

        if STATE.passed() * 10 > chunk_idx:
            draw_message(['{:4.4f}'.format(time.time()),
                          chunk_idx,
                          STATE.passed(),
                          ] + STATE.queue)
            draw_controllers()
            pygame.display.flip()
            chunk_idx += 1

        pass

        # time.sleep(0.001)


# %%
