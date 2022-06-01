# %%
import time
import random

from .buffer import SUSPECT_BUFFER
from .buffer import NON_TARGET_BUFFER

from .buffer import summary_buffers

from .logger import LOGGER
from .loop_manager import LOOP_MANAGER
from .constants import *

# %%

frame_rate_stats = dict(
    count=0,
    t0=time.time(),
    rate=-1,
    status='RSVP',  # RSVP | ERROR
)


def compute_frame_rate():
    t0 = frame_rate_stats['t0']
    t = time.time() - t0
    count = frame_rate_stats['count']
    rate = max(0, count-1) / t
    return rate


def draw_frame_rate():
    width = 1

    if frame_rate_stats['status'] == 'RSVP':
        color = WHITE
    else:
        color = RED

    background = None
    antialias = True

    top = int(CFG['centerPatch']['top'])
    left = int(CFG['centerPatch']['left'])

    t0 = frame_rate_stats['t0']
    t = time.time() - t0
    count = frame_rate_stats['count']
    rate = compute_frame_rate()
    frame_rate_stats['rate'] = rate

    status = frame_rate_stats['status']

    string = '| {} | Count: {} | Pass: {:0.3f} | Rate: {:0.2f} |'.format(
        status, count, t, rate)

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
        CAPTURE=['__CAPTURE__', -1],
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


if CFG['RSVP']['rate'] == '10':
    k = 40
    kk_min = 10
    kk_max = 30

if CFG['RSVP']['rate'] == '5':
    k = 20
    kk_min = 5
    kk_max = 15

def mk_chunk():
    # Randomly select non target surfaces with k times
    # The kk-th surface will be replaced by the suspect surface
    # The kk value will be set to -1 if there is not any suspect surface,
    # to make sure the replacement will never happen
    pairs = NON_TARGET_BUFFER.get_random(k=k)
    if pairs is None:
        frame_rate_stats['status'] = 'ERROR - no capture'

    if frame_rate_stats['status'] == 'RSVP':
        suspect_pair = SUSPECT_BUFFER.pop()
        if suspect_pair is None:
            kk = -1
        else:
            kk = random.randint(kk_min, kk_max)
            suspect_pair = suspect_pair[0]

    SUSPECT_BUFFER.append(suspect_pair)

    LOGGER.debug('Select idx:{} for suspect pair'.format(suspect_pair.idx))

    return pairs, suspect_pair, kk


def rsvp_loop():
    LOGGER.info('RSVP loop started')
    frame_rate_stats['status'] = 'RSVP'

    pairs, suspect_pair, kk = mk_chunk()

    offset = 0

    position = (
        int(CFG['centerPatch']['left']),
        int(CFG['centerPatch']['top'])
    )

    frame_rate_stats['t0'] = time.time()
    frame_rate_stats['count'] = 0

    controllers = draw_controllers()
    while True:
        SCREEN.fill(BLACK)
        draw_controllers()

        if not LOOP_MANAGER.get() == 'RSVP':
            LOGGER.info('Escape from RSVP loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            if event.type == pygame.MOUSEBUTTONUP:
                for cmd in controllers:
                    if controllers[cmd][1].contains(event.pos, (1, 1)):
                        LOGGER.info('Event: MouseButtonDown: {}'.format(cmd))
                        if cmd == 'CAPTURE':
                            LOOP_MANAGER.set('CAPTURE')

                        if cmd == 'MAIN':
                            LOOP_MANAGER.set('MAIN')

        if (time.time() - frame_rate_stats['t0']) * RATE > frame_rate_stats['count']:
            if frame_rate_stats['status'] == 'RSVP':
                if frame_rate_stats['count'] > k + offset:
                    LOGGER.error('RSVP_LOOP is running incorrect since {} > {}'.format(
                        frame_rate_stats['count'], k + offset))
                    break

                if frame_rate_stats['count'] == k + offset:
                    # The chunk is finished
                    # Start the next chunk
                    offset += k
                    pairs, suspect_pair, kk = mk_chunk()

                if frame_rate_stats['count'] == kk + offset:
                    pair = suspect_pair
                    LOGGER.debug(
                        'Display suspect picture: {}'.format(pair.idx))
                else:
                    pair = pairs[frame_rate_stats['count'] - offset]

                frame_rate_stats['count'] += 1

                SCREEN.blit(pair.surface, position)

            draw_frame_rate()
            draw_summary()
            pygame.display.flip()

# %%
