# %%
import time

from .toolbox import frame2surface, Controller, Pair

from .buffer import NON_TARGET_BUFFER

from .buffer import draw_summary

from .toggle_options import TOGGLE_OPTION
from .video_flow import VIDEO_FLOW, known_path
from .logger import LOGGER
from .loop_manager import LOOP_MANAGER
from .constants import *

# %%
frame_rate_stats = dict(
    count=0,
    t0=time.time(),
    record=False,
    rate=-1,
    name='[not-set]'
)


def compute_frame_rate():
    t0 = frame_rate_stats['t0']
    t = time.time() - t0
    count = frame_rate_stats['count']
    rate = max(0, count-1) / t
    return rate


def draw_frame_rate(error=''):
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
    name = frame_rate_stats['name']
    rate = compute_frame_rate()
    frame_rate_stats['rate'] = rate

    if frame_rate_stats['record']:
        record = 'REC'
    else:
        record = '---'

    if error is not '':
        record = error
        color = RED

    string = '| {} | Name: {} | Count: {} | Pass: {:0.3f} | Rate: {:0.2f} |'.format(
        record, name, count, t, rate)

    text = FONT.render(string, antialias, color, background)
    rect = text.get_rect()
    rect.height *= 1.1
    rect.center = (left + rect.width/2, top + rect.height/2)

    SCREEN.blit(text, rect)
    pygame.draw.rect(SCREEN, color, rect, width=width)

# %%


controllers = dict(
    MAIN=['__MAIN__', -1],
    RSVP=['__RSVP__', -1],
    REC=['__REC__', -1],
)

for name in known_path:
    s = '[{}]'.format(name)
    controllers[s] = [s, -1]

# controllers = draw_controllers(controllers)

controller = Controller(controllers, 'Capture')


# %%
def capture_loop():
    LOGGER.info('Capture loop started')

    # VIDEO_FLOW.connect()
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

    while True:
        SCREEN.fill(BLACK)
        # draw_controllers(controllers)
        controller.draw()
        TOGGLE_OPTION.draw()

        if not LOOP_MANAGER.get() == 'CAPTURE':
            LOGGER.info('Escape from capture loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            cmd = controller.check(event)
            TOGGLE_OPTION.check(event)

            if cmd == 'MAIN':
                LOOP_MANAGER.set('MAIN')

            if cmd == 'REC':
                frame_rate_stats['record'] = not frame_rate_stats['record']
                LOGGER.debug(
                    'Frame rate stats changes: {}'.format(frame_rate_stats))

            if cmd == 'RSVP':
                LOOP_MANAGER.set('RSVP')

            if cmd is not None:
                if cmd.startswith('[') and cmd.endswith(']'):
                    name = cmd[1:-1]
                    VIDEO_FLOW.connect(name)

        if (time.time() - frame_rate_stats['t0']) * RATE > frame_rate_stats['count']:
            frame_rate_stats['count'] += 1
            frame_rate_stats['name'] = VIDEO_FLOW.name

            frame = VIDEO_FLOW.get()

            if frame is not None:
                surface = frame2surface(frame, size)

                if frame_rate_stats['record']:
                    pair = Pair(frame, surface)
                    NON_TARGET_BUFFER.append(pair)

                SCREEN.blit(surface, position)
                draw_frame_rate()
            else:
                draw_frame_rate(error='No videoFlow')

            if TOGGLE_OPTION.options['SUM'][2]:
                draw_summary()

            pygame.display.flip()


# %%
