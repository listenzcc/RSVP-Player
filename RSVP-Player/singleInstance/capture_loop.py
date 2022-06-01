# %%
import time

from .toolbox import frame2surface, Pair

from .buffer import NON_TARGET_BUFFER

from .buffer import summary_buffers

from .video_flow import VIDEO_FLOW
from .logger import LOGGER
from .loop_manager import LOOP_MANAGER
from .constants import *

# %%
frame_rate_stats = dict(
    count=0,
    t0=time.time(),
    record=False,
    rate=-1,
)


def compute_frame_rate():
    t0 = frame_rate_stats['t0']
    t = time.time() - t0
    count = frame_rate_stats['count']
    rate = max(0, count-1) / t
    return rate


def draw_frame_rate():
    width = 1

    if frame_rate_stats['record']:
        color = RED
    else:
        color = WHITE

    background = None
    antialias = True

    top = int(CFG['centerPatch']['top'])
    left = int(CFG['centerPatch']['left'])

    t0 = frame_rate_stats['t0']
    t = time.time() - t0
    count = frame_rate_stats['count']
    rate = compute_frame_rate()
    frame_rate_stats['rate'] = rate

    if frame_rate_stats['record']:
        record = 'REC'
    else:
        record = '---'

    string = '| {} | Count: {} | Pass: {:0.3f} | Rate: {:0.2f} |'.format(
        record, count, t, rate)

    text = FONT.render(string, antialias, color, background)
    rect = text.get_rect()
    rect.height *= 1.1
    rect.center = (left + rect.width/2, top + rect.height/2)

    SCREEN.blit(text, rect)
    pygame.draw.rect(SCREEN, color, rect, width=width)

# %%


def draw_controllers():
    width = 1
    color = WHITE
    background = None
    antialias = True

    top = 30
    left = int(CFG['screen']['width']) / 10
    _left = 30

    controllers = dict(
        MAIN=['__MAIN__', -1],
        RSVP=['__RSVP__', -1],
        REC=['__REC__', -1]
    )

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
def capture_loop():
    LOGGER.info('Capture loop started')

    VIDEO_FLOW.connect()
    size = (
        int(CFG['picture']['width']),
        int(CFG['picture']['height'])
    )
    position = (
        int(CFG['centerPatch']['left']),
        int(CFG['centerPatch']['top'])
    )
    frame_rate_stats['t0'] = time.time()
    frame_rate_stats['count'] = 0
    frame_rate_stats['record'] = False

    controllers = draw_controllers()
    while True:
        SCREEN.fill(BLACK)
        draw_controllers()

        if not LOOP_MANAGER.get() == 'CAPTURE':
            LOGGER.info('Escape from capture loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            if event.type == pygame.MOUSEBUTTONUP:
                for cmd in controllers:
                    # Received MOUSEBUTTONDOWN event on cmd
                    if controllers[cmd][1].contains(event.pos, (1, 1)):
                        LOGGER.info('Event: MouseButtonDown: {}'.format(cmd))
                        if cmd == 'MAIN':
                            LOOP_MANAGER.set('MAIN')

                        if cmd == 'REC':
                            frame_rate_stats['record'] = not frame_rate_stats['record']
                            LOGGER.debug(
                                'Frame rate stats changes: {}'.format(frame_rate_stats))

                        if cmd == 'RSVP':
                            LOOP_MANAGER.set('RSVP')

        if (time.time() - frame_rate_stats['t0']) * RATE > frame_rate_stats['count']:
            frame_rate_stats['count'] += 1
            frame = VIDEO_FLOW.get()
            surface = frame2surface(frame, size)

            if frame_rate_stats['record']:
                pair = Pair(frame, surface)
                NON_TARGET_BUFFER.append(pair)

            SCREEN.blit(surface, position)
            draw_frame_rate()
            draw_summary()
            pygame.display.flip()


# %%
