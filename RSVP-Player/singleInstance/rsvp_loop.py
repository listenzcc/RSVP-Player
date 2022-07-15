# %%
import time
import random

from .toolbox import Controller
from .toggle_options import TOGGLE_OPTION

from .buffer import SUSPECT_BUFFER
from .buffer import CHUNK_COUNTER
from .buffer import NON_TARGET_BUFFER
from .buffer import INTER_BUFFER

from .buffer import draw_summary

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

    if frame_rate_stats['status'].startswith('RSVP'):
        color = BLACK
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


controllers = dict(
    MAIN=['__MAIN__', -1],
    CAPTURE=['__CAPTURE__', -1],
)

controller = Controller(controllers, 'RSVP')


# %%

'''
kk is the location of the suspect-target picture

The chunk lasts 5.0 seconds.
The first 0.5 seconds contain no suspect-target pictures
The suspect-targets are only allowed to be displayed in between 0.5 to 2.0 seconds
'''

if CFG['RSVP']['rate'] == '10':
    rsvp_fs = 10
    chunk_length = 50 + 2
    kk_min = 5
    kk_max = 20

if CFG['RSVP']['rate'] == '5':
    rsvp_fs = 5
    chunk_length = 25 + 2
    kk_min = 3
    kk_max = 10

CHUNK_COUNTER.reset()
# %%


def mk_chunk():

    pairs2 = None

    # Single
    if TOGGLE_OPTION.options['UNT'][2]:
        # Use non target pictures
        pairs = NON_TARGET_BUFFER.get_random(k=chunk_length)
        if pairs is None:
            frame_rate_stats['status'] = 'ERROR - no non-target'
            LOGGER.warning('Can not find captured pictures for rsvp display')
            return None, None

        frame_rate_stats['status'] = 'RSVP(UNT)'
        suspect_pair = SUSPECT_BUFFER.pop()
        # black_pair = BLACK_BUFFER.pairs[0]

        if suspect_pair is not None:
            kk = random.randint(kk_min, kk_max)
            pairs[kk] = suspect_pair[0]
            LOGGER.debug(
                'Select idx:{}, {} for suspect pair'.format(suspect_pair[0].idx, kk))

        # for j in range(kk_max+1, chunk_length):
        #     pairs[j] = black_pair[0]
        #     LOGGER.debug('Replace the {}-th pair with black picture'.format(j))

    # Dual
    if TOGGLE_OPTION.options['UNT'][2] and CFG['RSVP']['mode'] == 'dual':
        # Use non target pictures
        pairs2 = NON_TARGET_BUFFER.get_random(k=10)
        for j in range(chunk_length-10):
            pairs2.append(pairs[j])

    # Single
    if not TOGGLE_OPTION.options['UNT'][2]:
        # Not use non target pictures
        pairs = []
        frame_rate_stats['status'] = 'RSVP(SUS)'
        for kk in range(chunk_length):
            s = SUSPECT_BUFFER.pop()
            if s is None:
                frame_rate_stats['status'] = 'ERROR - no suspect'
                LOGGER.warning(
                    'Can not find any suspect pair, and the option is not use non-target-pictures')
                return None, None
            SUSPECT_BUFFER.append(s[0])
            pairs.append(s[0])

    # Dual
    if not TOGGLE_OPTION.options['UNT'][2] and CFG['RSVP']['mode'] == 'dual':
        # Not use non target pictures
        pairs2 = []
        frame_rate_stats['status'] = 'RSVP(SUS)'
        for kk in range(chunk_length):
            s = SUSPECT_BUFFER.pop()
            if s is None:
                frame_rate_stats['status'] = 'ERROR - no suspect 2'
                LOGGER.warning(
                    'Can not find any suspect pair 2, and the option is not use non-target-pictures')
                return None, None
            SUSPECT_BUFFER.append(s[0])
            pairs2.append(s[0])

    return pairs, pairs2


def mk_chunk_old():
    '''
    Randomly select non target surfaces with k times
    The kk-th surface will be replaced by the suspect surface
    The kk value will be set to -1 if there is not any suspect surface,
    to make sure the replacement will never happen
    '''

    if TOGGLE_OPTION.options['UNT'][2]:
        # Use non target pictures
        frame_rate_stats['status'] = 'RSVP(UNT)'
        pairs = NON_TARGET_BUFFER.get_random(k=chunk_length)
        if pairs is None:
            frame_rate_stats['status'] = 'ERROR - no capture'
            LOGGER.warning('Can not find captured pictures for rsvp display')
            return None, None, None

        kk = -1
        suspect_pair = SUSPECT_BUFFER.pop()

        if suspect_pair is not None:
            kk = random.randint(kk_min, kk_max)
            suspect_pair = suspect_pair[0]

        SUSPECT_BUFFER.append(suspect_pair)

        if suspect_pair is not None:
            LOGGER.debug(
                'Select idx:{} for suspect pair'.format(suspect_pair.idx))

        suspect_pair = [suspect_pair]
        kk = [kk]

    if not TOGGLE_OPTION.options['UNT'][2]:
        # Not use non target pictures
        frame_rate_stats['status'] = 'RSVP(SUS)'

        # We do not need pairs
        pairs = []

        # We need every pair to be the suspect pair
        kk = [e for e in range(chunk_length)]

        # We need the suspect_pair for chunk_length elements
        suspect_pair = []
        for _ in range(chunk_length):
            s = SUSPECT_BUFFER.pop()
            if s is None:
                frame_rate_stats['status'] = 'ERROR - no suspect'
                LOGGER.warning(
                    'Can not find any suspect pair, and the option is not use non-target-pictures')
                return None, None, None

            suspect_pair.append(s[0])
            SUSPECT_BUFFER.append(s[0])

        random.shuffle(suspect_pair)

    # Convert the suspect_pair and kk into list for .pop() method
    # The kk has one more element in the 1st position,
    # it means it will not be used.
    suspect_pair.reverse()
    kk.append(-1)
    kk.reverse()

    return pairs, suspect_pair, kk


def check_inter():
    '''
    Check INTER_BUFFER, if it contains pairs, prepare to enter to the inter_loop.
    '''
    loop_name = 'RSVP'

    if not TOGGLE_OPTION.options['INT'][2]:
        # If not allow interrupted
        INTER_BUFFER.default()
        return loop_name

    if len(INTER_BUFFER.pairs) > 0:
        loop_name = 'INTER'

    return loop_name


def rsvp_loop():

    LOOP_MANAGER.set(check_inter())
    if not LOOP_MANAGER.get() == 'RSVP':
        LOGGER.info('Leave the rsvp loop, reason: {}'.format(
            LOOP_MANAGER.get()))
        return

    LOGGER.info('RSVP loop started')
    frame_rate_stats['status'] = 'RSVP'

    pairs, pairs2 = mk_chunk()

    offset = 0

    position = (
        int(CFG['centerPatch']['left']),
        int(CFG['centerPatch']['top'])
    )

    position2 = (
        int(CFG['subPatch']['left']),
        int(CFG['subPatch']['top'])
    )

    frame_rate_stats['t0'] = time.time()
    frame_rate_stats['count'] = 0

    while True:
        SCREEN.fill(BLACK)
        controller.draw()
        TOGGLE_OPTION.draw()

        if not LOOP_MANAGER.get() == 'RSVP':
            LOGGER.info('Escape from RSVP loop')
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT_PYGAME()

            cmd = controller.check(event)
            TOGGLE_OPTION.check(event)

            if cmd == 'CAPTURE':
                LOOP_MANAGER.set('CAPTURE')

            if cmd == 'MAIN':
                LOOP_MANAGER.set('MAIN')

        '''
        The variables mean:
        - chunk_length: The length of the chunk;
        - kk: The idx of the suspect picture;
        - pairs: The non-target pairs;
        - suspect_pair: The target pair;
        - offset: The next chunk is append when the chunk is finished **immediately**,
                  so the offset is the offset of the beginning index.
        '''

        if (time.time() - frame_rate_stats['t0']) * RATE > frame_rate_stats['count']:
            # Status is ERROR
            if not frame_rate_stats['status'].startswith('RSVP'):
                LOGGER.debug('Switch from None to RSVP')
                # pairs, suspect_pair, kk = mk_chunk()
                pairs, pairs2 = mk_chunk()
                if frame_rate_stats['status'].startswith('RSVP'):
                    offset = 0
                    frame_rate_stats['t0'] = time.time()
                    frame_rate_stats['count'] = 0
                    continue

            # Status changed from UNT to SUS
            if frame_rate_stats['status'] == 'RSVP(UNT)' and not TOGGLE_OPTION.options['UNT'][2]:
                LOGGER.debug('Switch from UNT to SUS')
                # pairs, suspect_pair, kk = mk_chunk()
                pairs, pairs2 = mk_chunk()
                if frame_rate_stats['status'].startswith('RSVP'):
                    offset = 0
                    frame_rate_stats['t0'] = time.time()
                    frame_rate_stats['count'] = 0
                    continue

            # Status changed from SUS to UNT
            if frame_rate_stats['status'] == 'RSVP(SUS)' and TOGGLE_OPTION.options['UNT'][2]:
                LOGGER.debug('Switch from SUS to UNT')
                # pairs, suspect_pair, kk = mk_chunk()
                pairs, pairs2 = mk_chunk()
                if frame_rate_stats['status'].startswith('RSVP'):
                    offset = 0
                    frame_rate_stats['t0'] = time.time()
                    frame_rate_stats['count'] = 0
                    continue

            if frame_rate_stats['status'].startswith('RSVP'):

                # Something wrong is happening,
                # we detect that the counting system is totally out of control
                if frame_rate_stats['count'] > chunk_length + offset:
                    LOGGER.error('RSVP_LOOP is running incorrect since {} > {}'.format(
                        frame_rate_stats['count'], chunk_length + offset))
                    break

                # The chunk is finished
                if frame_rate_stats['count'] == chunk_length + offset:
                    # The chunk is finished
                    # Start the next chunk
                    # or Enter into the inter_loop

                    LOGGER.info('Rsvp loop: chunk stops')

                    LOOP_MANAGER.set(check_inter())
                    if not LOOP_MANAGER.get() == 'RSVP':
                        LOGGER.info('Leave the rsvp loop, reason: {}'.format(
                            LOOP_MANAGER.get()))
                        return

                    offset += chunk_length
                    # pairs, suspect_pair, kk = mk_chunk()
                    pairs, pairs2 = mk_chunk()
                    if not frame_rate_stats['status'].startswith('RSVP'):
                        continue

                if frame_rate_stats['count'] == offset:
                    # Chunk starts
                    PARALLEL.send(16)
                    LOGGER.debug('Chunk starts: send 16 tag')

                if frame_rate_stats['count'] == chunk_length + offset - 1:
                    # Chunk stops
                    PARALLEL.send(20)
                    CHUNK_COUNTER.add()
                    LOGGER.debug('Chunk stops: send 20 tag')
                    if CHUNK_COUNTER.value % CHUNK_COUNTER.limit == 0:
                        PARALLEL.send(25)
                        LOGGER.debug('Block stops: send 25 tag')

                pair = pairs[frame_rate_stats['count'] - offset]
                if pairs2 is not None:
                    pair2 = pairs2[frame_rate_stats['count'] - offset]
                else:
                    pair2 = None

                if pair.idx > 0:
                    # PARALLEL.send(pair.idx)
                    PARALLEL.send(1)
                    LOGGER.debug(
                        'Display suspect picture (1): {}'.format(pair.idx))
                else:
                    if frame_rate_stats['count'] == offset:
                        LOGGER.debug(
                            'Ignore the 2 tag since the 16 is on the way')
                    else:
                        PARALLEL.send(2, verbose=False)
                    pass

                if pair2 is not None:
                    if pair2.idx > 0:
                        LOGGER.debug(
                            'Display suspect picture (2): {}'.format(pair2.idx))

                # !!! Append the pair into the INTER_BUFFER
                # !!! Only for development
                # if frame_rate_stats['count'] - offset == 3 or pair.idx > 0:
                #     INTER_BUFFER.append(pair)
                # if pair2 is not None:
                #     if pair2.idx > 0:
                #         INTER_BUFFER.append(pair2)

                frame_rate_stats['count'] += 1

                SCREEN.blit(pair.surface, position)
                if CFG['RSVP']['mode'] == 'dual':
                    SCREEN.blit(pair2.surface, position2)

            if TOGGLE_OPTION.options['OSD'][2]:
                draw_frame_rate()

            if TOGGLE_OPTION.options['SUM'][2]:
                draw_summary()

            pygame.display.flip()

# %%
