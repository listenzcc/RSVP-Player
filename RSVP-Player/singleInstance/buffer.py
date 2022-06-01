# %%
import random
from .logger import LOGGER
from .constants import *

# %%
# Raw buffer


class RawBuffer(object):
    def __init__(self):
        self.limit = CFG['buffer']['maxSize']
        self.pairs = []

    def insert(self, pair):
        self.pairs.insert(0, pair)

    def append(self, pair):
        self.pairs.append(pair)

    def refresh(self):
        self.valid = [e for e in self.pairs if e.count[1] == 1]
        self.frame_count = len(self.pairs)
        self.surface_count = len(self.valid)

# %%
# Non target buffer


class NonTargetBuffer(RawBuffer):
    def __init__(self):
        super(NonTargetBuffer, self).__init__()
        LOGGER.info('NonTargetBuffer initialized')
        pass

    def get_random(self, k=100):
        self.refresh()

        if self.surface_count == 0:
            LOGGER.error('NonTargetBuffer has no surface. Run CAPTURE first')
            return

        if k > self.surface_count:
            LOGGER.warning('NonTargetBuffer can not random_get enough surfaces, since {} > {}'.format(
                k, self.surface_count))
            LOGGER.warning(
                'NonTargetBuffer random_get is using choices with-replacement')
            return random.choices(self.valid, k=k)

        return random.sample(self.valid, k=k)

    def get_all(self):
        self.refresh()
        LOGGER.debug('NonTargetBuffer gives all the valid surfaces')
        return self.valid


NON_TARGET_BUFFER = NonTargetBuffer()

# %%
# Suspect buffer


class SuspectBuffer(RawBuffer):
    def __init__(self):
        super(SuspectBuffer, self).__init__()
        LOGGER.info('SuspectBuffer initialized')
        pass

    def pop(self):
        self.refresh()

        if self.surface_count == 0:
            LOGGER.error(
                'SuspectBuffer can not pop, since the surface buffer is empty')
            return

        idx = self.valid[0].idx

        return self.pop_idx(idx)

    def pop_idx(self, idx):
        self.refresh()
        select = [e for e in self.valid if e.idx == idx]

        if len(select) == 0:
            LOGGER.error('SuspectBuffer can not find idx: {}'.format(idx))
            return

        if len(select) > 1:
            LOGGER.warning(
                'SuspectBuffer find {} pairs for idx: {}'.format(len(select), idx))

        LOGGER.debug('SuspectBuffer pop idx: {}'.format(idx))

        self._remove_idx(idx)

        return select

    def _remove_idx(self, idx):
        n = len(self.pairs)
        self.pairs = [e for e in self.pairs if not e.idx == idx]
        self.refresh()
        LOGGER.debug(
            'Pop idx: {}, size changes: {} -> {}'.format(idx, n, self.frame_count))


SUSPECT_BUFFER = SuspectBuffer()

# %%


class InterBuffer(RawBuffer):
    def __init__(self):
        super(InterBuffer, self).__init__()
        LOGGER.info('InterruptBuffer initialized')
        pass

    def pop(self):
        if len(self.pairs) == 0:
            LOGGER.error(
                'InterruptBuffer can not pop, since the pairs are empty')
            return

        first = self.pairs.pop(0)

        self.refresh()

        LOGGER.debug('InterruptBuffer pops 1 pairs')

        return first


INTER_BUFFER = InterBuffer()


# %%


def summary_buffers():
    NON_TARGET_BUFFER.refresh()
    SUSPECT_BUFFER.refresh()
    INTER_BUFFER.refresh()
    output = [
        '| Summary           {:4s} {:4s} |'.format('', ''),
        '| Buffer Name     | {:4s}|{:4s} |'.format('frm', 'srf'),
        # Non target buffer
        '| NonTargetBuffer | {:4d}|{:4d} |'.format(
            NON_TARGET_BUFFER.frame_count, NON_TARGET_BUFFER.surface_count),
        # Suspect buffer
        '| SuspectBuffer   | {:4d}|{:4d} |'.format(
            SUSPECT_BUFFER.frame_count, SUSPECT_BUFFER.surface_count),
        # Interrupt buffer
        '| InterruptBuffer | {:4d}|{:4d} |'.format(
            INTER_BUFFER.frame_count, INTER_BUFFER.surface_count),
    ]

    return output
