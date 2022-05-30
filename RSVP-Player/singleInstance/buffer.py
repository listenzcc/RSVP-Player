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

    def append(self, pair):
        self.pairs.append(pair)

    def count(self):
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
        self.count()

        if k > self.surface_count:
            LOGGER.warning('NonTargetBuffer can not random_get enough surfaces, since {} > {}'.format(
                k, self.surface_count))
            LOGGER.warning(
                'NonTargetBuffer random_get is using choices with-replacement')
            return random.choices(self.valid, k=k)

        return random.sample(self.valid, k=k)

    def get_all(self):
        self.count()
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
        self.count()

        if self.surface_count == 0:
            LOGGER.error('Can not pop, since the surface buffer is empty')
            return

        idx = self.valid[0].idx

        return self.pop_idx(idx)

    def pop_idx(self, idx):
        self.count()
        select = [e for e in self.valid if e.idx == idx]

        if len(select) == 0:
            LOGGER.error('Can not find idx: {}'.format(idx))
            return

        if len(select) > 1:
            LOGGER.warning(
                'Find {} pairs for idx: {}'.format(len(select), idx))

        LOGGER.debug('Pop idx: {}'.format(idx))

        self._remove_idx(idx)

        return select

    def _remove_idx(self, idx):
        n = len(self.pairs)
        self.pairs = [e for e in self.pairs if not e.idx == idx]
        self.count()
        LOGGER.debug(
            'Pop idx: {}, size changes: {} -> {}'.format(idx, n, self.frame_count))


SUSPECT_BUFFER = SuspectBuffer()


# %%


def summary_buffers():
    NON_TARGET_BUFFER.count()
    SUSPECT_BUFFER.count()
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
        '| InterruptBuffer | {:4d}|{:4d} |'.format(0, 0)
    ]

    return output
