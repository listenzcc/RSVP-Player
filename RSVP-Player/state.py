'''
FileName: state.py
Author: Chuncheng
Version: V0.0
Purpose: State management for the project
'''

# %%
import time
from startup import LOGGER

# %%

states = dict(
    NONE='No state is defined',
    RSVP='Display the rsvp sequence',
    INTER='Interactive with the subject'
)

# %%


class State(object):
    def __init__(self, queue_limit=10):
        self.states = states
        self.last = 'NONE'
        self.current = 'NONE'
        self.queue = ['NONE'] * queue_limit
        LOGGER.info("State management initialized.")

    def set(self, state):
        assert state in self.states, 'State {} is undefined'.format(state)
        self.last = self.current
        self.current = state
        self.queue.insert(0, state)
        self.queue.pop()
        self.time = time.time()
        LOGGER.info("State changed: {} -> {}".format(self.last, self.current))

    def get(self):
        return self.current

    def passed(self):
        return time.time() - self.time


# %%
STATE = State()
